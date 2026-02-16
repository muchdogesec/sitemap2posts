import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import re
import argparse
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from fnmatch import fnmatch
from newspaper import Article
from htmldate import find_date
from email.utils import parsedate_to_datetime
from dateutil.parser import parse as parse_dt

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

lastmod_default = datetime.now(timezone.utc)

# Save the original default method
JSONEncoder_olddefault = json.JSONEncoder.default


# Define the new default method
def JSONEncoder_newdefault(self, obj):
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        return obj.isoformat()
    # Call the original method for other types
    return JSONEncoder_olddefault(self, obj)


# Replace the default method with the new one
json.JSONEncoder.default = JSONEncoder_newdefault


def make_dt_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC if it is naive."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fetch_url(url, timeout=10):
    """Fetch URL with error handling."""
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Sitemap2post/0.0.1 (+https://github.com/muchdogesec/sitemap2posts)"
            },
        )

        return response
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


def get_sitemaps_from_robots(url):
    """Extract sitemap URLs from robots.txt."""
    logging.info(f"Fetching robots.txt from {url}")
    robots_url = urljoin(url, "/robots.txt")
    response = fetch_url(robots_url)

    if not response or response.status_code != 200:
        logging.error(f"Failed to fetch robots.txt from {robots_url}")
        return []

    logging.info("Successfully fetched robots.txt")
    sitemaps = re.findall(r"Sitemap: (.*)", response.text, re.IGNORECASE)

    if not sitemaps:
        logging.error("No sitemaps found in robots.txt.")
    else:
        logging.info(f"Found {len(sitemaps)} sitemap(s) in robots.txt")

    return sitemaps


def parse_sitemap_content(soup, sitemap_url):
    """Parse sitemap XML content and return URLs with type indicator."""
    if soup.find("sitemapindex"):
        logging.info(f"{sitemap_url} is a sitemap index")
        sitemap_urls = [sitemap.text.strip() for sitemap in soup.find_all("loc")]
        logging.info(f"Found {len(sitemap_urls)} sitemap(s) in sitemap index")
        return sitemap_urls, True

    if soup.find("urlset"):
        logging.info(f"{sitemap_url} is a URL set")
        urls = []
        for url in soup.find_all("url"):
            loc = url.find("loc")
            lastmod = url.find("lastmod")
            if lastmod:
                lastmod = make_dt_utc(parse_dt(lastmod.text.strip()))
            if loc:
                urls.append((loc.text.strip(), lastmod))
        logging.info(f"Found {len(urls)} URL(s) in sitemap")
        return urls, False

    logging.warning(f"Unrecognized sitemap format for {sitemap_url}")
    return [], False


def get_sitemap_urls(sitemap_url):
    """Fetch and parse a sitemap URL."""
    logging.info(f"Fetching sitemap from {sitemap_url}")
    response = fetch_url(sitemap_url)

    if not response or not response.ok:
        reason = response.reason if response else "No response"
        logging.error(f"Failed to fetch sitemap from {sitemap_url}: {reason}")
        return [], False

    soup = BeautifulSoup(response.content, "lxml-xml")
    return parse_sitemap_content(soup, sitemap_url)


def dedupe_urls(url_list):
    logging.info("Deduplicating URLs")
    unique_urls = {}
    for url, lastmod, sitemap in url_list:
        if url not in unique_urls or (
            lastmod and unique_urls[url]["lastmod"] > lastmod
        ):
            unique_urls[url] = {"lastmod": lastmod, "sitemap": sitemap}
    logging.info(f"Deduplication complete, {len(unique_urls)} unique URLs remaining")
    return unique_urls


def get_post_title(url, check_404=False):
    """Fetch the title of a post from its URL.

    Args:
        url: The URL to fetch
        check_404: If True, return None for 404 responses instead of fetching title

    Returns:
        Tuple of (data, is_valid) where is_valid indicates if URL is not 404
    """
    logging.debug(f"Fetching post title from {url}")
    response = fetch_url(url)

    data = dict()

    if not response:
        logging.debug(f"Failed to fetch URL {url}")
        return None, False

    last_modified = response.headers.get("Last-Modified")
    if last_modified:
        data["modified_header"] = make_dt_utc(parsedate_to_datetime(last_modified))

    # Check for 404 if requested
    if check_404 and response.status_code == 404:
        logging.info(f"URL {url} returned 404. Excluding from results.")
        return None, False

    if response.status_code != 200:
        logging.debug(f"Failed to fetch URL {url}")
        return None, False

    article = Article(url)
    article.download(input_html=response.text)
    article.parse()
    data["title"] = article.title.strip()
    meta_keywords = [kw for kw in article.meta_keywords if kw.strip()]
    if meta_keywords:
        data["meta_keywords"] = meta_keywords
    if article.publish_date:
        data["publish_date"] = make_dt_utc(article.publish_date)
    if article.tags:
        data["tags"] = list(article.tags)
    if article.meta_description:
        data["meta_description"] = article.meta_description.strip()
    if article.authors:
        data["authors"] = "; ".join(article.authors)
    date = find_date(
        response.text,
        url=url,
        extensive_search=True,
        outputformat="%Y-%m-%dT%H:%M:%S%z",
    )
    if date:
        data["htmldate"] = make_dt_utc(datetime.fromisoformat(date))

    logging.debug(f"Successfully fetched title: {data['title']}")
    return data, True


def save_to_json(posts, output_filename="sitemap_posts.json"):
    for post in posts:
        if post["lastmod"] is None:
            post["lastmod"] = lastmod_default.isoformat()

    # Sort posts by sitemap first, and then by lastmod (newest first)
    sorted_posts = sorted(
        posts, key=lambda x: (x["sitemap"], x["lastmod"]), reverse=True
    )
    logging.info(f"Saving results to {output_filename}")
    try:
        with open(output_filename, "w", encoding="utf-8") as jsonfile:
            json.dump(sorted_posts, jsonfile, indent=4)
        logging.info(f"JSON saved successfully with {len(posts)} post(s)")
    except IOError as e:
        logging.error(f"Failed to save JSON to {output_filename}: {e}")


def is_date_after_min(lastmod_parsed, lastmod_min):
    """Check if parsed date is after the minimum date."""
    if lastmod_parsed.tzinfo is None:
        lastmod_min_naive = lastmod_min.replace(tzinfo=None)
        return lastmod_parsed >= lastmod_min_naive
    return lastmod_parsed >= lastmod_min


def should_skip_sitemap(sitemap, ignore_sitemaps):
    """Check if a sitemap should be skipped."""
    if ignore_sitemaps and sitemap in ignore_sitemaps:
        logging.info(f"Skipping sitemap {sitemap} as per ignore_sitemaps")
        return True
    return False


def collect_urls_from_sitemaps(sitemaps, ignore_sitemaps):
    """Collect all URLs from a list of sitemaps."""
    all_urls = []

    for sitemap in sitemaps:
        if should_skip_sitemap(sitemap, ignore_sitemaps):
            continue

        urls, is_sitemap_index = get_sitemap_urls(sitemap)

        if is_sitemap_index:
            for sub_sitemap in urls:
                if should_skip_sitemap(sub_sitemap, ignore_sitemaps):
                    continue

                sub_urls, _ = get_sitemap_urls(sub_sitemap)
                all_urls.extend(
                    [(url, lastmod, sub_sitemap) for url, lastmod in sub_urls]
                )
        else:
            all_urls.extend([(url, lastmod, sitemap) for url, lastmod in urls])

    return all_urls


def filter_urls_by_lastmod(urls, lastmod_min):
    """Filter URLs based on lastmod date."""
    if not lastmod_min:
        return urls

    logging.info(f"Filtering URLs with lastmod on or after {lastmod_min.date()}")
    filtered = {}

    for url, data in urls.items():
        if data["lastmod"]:
            parsed_lastmod = data["lastmod"]
            if parsed_lastmod and not is_date_after_min(parsed_lastmod, lastmod_min):
                continue
        filtered[url] = data

    return filtered


def filter_urls_by_base(urls, base_url):
    """Filter URLs to only include those starting with base URL."""
    return {url: data for url, data in urls.items() if url.startswith(base_url)}


def url_matches_pattern(url, pattern):
    return fnmatch(url, pattern)


def filter_urls_by_paths(urls, ignore_paths=None, allow_paths=None):
    """Filter URLs based on ignore and allow path lists (supports glob patterns)."""
    filtered = urls

    # Apply allow list first (if specified, only keep URLs that match)
    if allow_paths:
        logging.info("Applying --path_allow_list filter (supports glob patterns)")
        filtered = {
            url: data
            for url, data in filtered.items()
            if any(url_matches_pattern(url, path) for path in allow_paths)
        }
        logging.info(
            f"{len(filtered)} URL(s) remain after applying --path_allow_list filter"
        )

    # Apply ignore list (remove URLs that match)
    if ignore_paths:
        logging.info("Applying --path_ignore_list filter (supports glob patterns)")
        filtered = {
            url: data
            for url, data in filtered.items()
            if not any(url_matches_pattern(url, path) for path in ignore_paths)
        }
        logging.info(
            f"{len(filtered)} URL(s) remain after applying --path_ignore_list filter"
        )

    return filtered


def fetch_post_titles(urls, remove_404_records=False):
    """Fetch titles for all URLs in parallel.

    Args:
        urls: Dictionary of URLs with their metadata
        remove_404_records: If True, exclude URLs that return 404

    Returns:
        List of post dictionaries
    """
    posts = []

    if remove_404_records:
        logging.info("Fetching post titles (excluding 404 responses)...")
    else:
        logging.info("Fetching post titles...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_post_title, url, remove_404_records): url
            for url in urls
        }
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                html_data, is_valid = future.result()

                # Skip if 404 and we're filtering them out
                if remove_404_records and not is_valid:
                    continue

                # Skip if title is None (404 case)
                if html_data is None:
                    continue

                posts.append(
                    {
                        "url": url,
                        "lastmod": urls[url]["lastmod"],
                        "sitemap": urls[url]["sitemap"],
                        **html_data,
                    }
                )
            except Exception as e:
                logging.error(f"Error fetching title for URL {url}: {e}")

    if remove_404_records:
        logging.info(
            f"{len(posts)} valid post(s) after fetching titles and excluding 404s"
        )
    else:
        logging.info(f"{len(posts)} post(s) fetched")

    return posts


def sitemap2posts(
    blog_url,
    sitemap_urls=None,
    lastmod_min=None,
    path_ignore_list=None,
    path_allow_list=None,
    ignore_sitemaps=None,
    remove_404_records=False,
):
    """Main function to crawl sitemaps and extract post information."""
    lastmod_min = lastmod_min and make_dt_utc(lastmod_min)

    if not sitemap_urls:
        logging.info("Using sitemaps from robots.txt")
        sitemap_urls = get_sitemaps_from_robots(blog_url)
    if not sitemap_urls:
        logging.error(
            "No sitemaps are defined in this website's robots.txt file, so it cannot be crawled."
        )
        return []

    # Collect URLs from all sitemaps
    all_urls = collect_urls_from_sitemaps(sitemap_urls, ignore_sitemaps)

    # Deduplicate URLs
    deduped_urls = dedupe_urls(all_urls)

    # Apply filters
    filtered_urls = filter_urls_by_base(deduped_urls, blog_url)
    filtered_urls = filter_urls_by_lastmod(filtered_urls, lastmod_min)
    filtered_urls = filter_urls_by_paths(
        filtered_urls, path_ignore_list, path_allow_list
    )

    if not filtered_urls:
        logging.warning("No URLs to process after applying filters.")
        return []

    # Fetch post titles (404 check is done during fetch if remove_404_records is True)
    posts = fetch_post_titles(filtered_urls, remove_404_records)

    if not posts:
        logging.warning("No posts to save after fetching titles.")
    return posts


def parse_cli_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Retrieve blog posts from sitemap.",
        epilog="""Examples:
  robots mode:      python sitemap2posts.py https://example.com/blog/
  sitemap_urls mode: python sitemap2posts.py https://example.com/blog/ --sitemap_urls https://example.com/sitemap1.xml https://example.com/sitemap2.xml
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "blog_url",
        type=str,
        help="Blog URL to extract posts from",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="sitemap_posts.json",
        help="Output JSON file name (default: sitemap_posts.json)",
    )
    parser.add_argument(
        "--sitemap_urls",
        type=str,
        nargs="+",
        help="One or more sitemap URLs to crawl directly (automatically uses sitemap_urls mode)",
    )
    parser.add_argument(
        "--lastmod_min",
        type=datetime.fromisoformat,
        default=None,
        metavar="YYYY-MM-DD",
        help="Filter URLs with lastmod date on or after (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--path_ignore_list",
        type=str,
        nargs="+",
        default=[],
        help="Path patterns to ignore (supports glob patterns). Examples: /blog/author '*/tag/*' 'https://example.com/*/archive'",
    )
    parser.add_argument(
        "--path_allow_list",
        type=str,
        nargs="+",
        default=[],
        help="Path patterns to allow (supports glob patterns). Only URLs matching these patterns will be included. Examples: /blog/post/* '*/2024/*'",
    )
    parser.add_argument(
        "--ignore_sitemaps",
        type=str,
        nargs='+',
        default=[],
        help="Comma-separated list of specific sitemap URLs to ignore",
    )
    parser.add_argument(
        "--remove_404_records",
        action="store_true",
        help="Exclude URLs that return a 404 status code.",
    )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_cli_arguments()


    # Call the function with the URLs and other parameters from CLI input
    posts = sitemap2posts(
        args.blog_url,
        sitemap_urls=args.sitemap_urls,
        lastmod_min=args.lastmod_min,
        path_ignore_list=args.path_ignore_list,
        path_allow_list=args.path_allow_list,
        ignore_sitemaps=args.ignore_sitemaps,
        remove_404_records=args.remove_404_records,
    )

    save_to_json(posts, args.output)
    logging.info("Sitemap crawling completed successfully")
