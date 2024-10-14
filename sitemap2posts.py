import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse
import re
import argparse
import logging
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_sitemaps_from_robots(url):
    logging.info(f"Fetching robots.txt from {url}")
    robots_url = urljoin(url, '/robots.txt')
    try:
        response = requests.get(robots_url, timeout=10)
    except requests.RequestException as e:
        logging.error(f"Error fetching robots.txt from {robots_url}: {e}")
        return []
        
    if response.status_code == 200:
        logging.info("Successfully fetched robots.txt")
        sitemaps = re.findall(r'Sitemap: (.*)', response.text, re.IGNORECASE)
        if not sitemaps:
            logging.error("No sitemaps found in robots.txt.")
        else:
            logging.info(f"Found {len(sitemaps)} sitemap(s) in robots.txt")
        return sitemaps
    else:
        logging.error(f"Failed to fetch robots.txt from {robots_url}, status code: {response.status_code}")
        return []

def get_sitemap_urls(sitemap_url):
    logging.info(f"Fetching sitemap from {sitemap_url}")
    try:
        response = requests.get(sitemap_url, timeout=10)
    except requests.RequestException as e:
        logging.error(f"Error fetching sitemap from {sitemap_url}: {e}")
        return [], False
        
    if response.status_code != 200:
        logging.error(f"Failed to fetch sitemap from {sitemap_url}, status code: {response.status_code}")
        return [], False
    
    soup = BeautifulSoup(response.content, 'lxml-xml')
    if soup.find('sitemapindex'):
        logging.info(f"{sitemap_url} is a sitemap index")
        sitemap_urls = [sitemap.text.strip() for sitemap in soup.find_all('loc')]
        logging.info(f"Found {len(sitemap_urls)} sitemap(s) in sitemap index")
        return sitemap_urls, True
    elif soup.find('urlset'):
        logging.info(f"{sitemap_url} is a URL set")
        urls = []
        for url in soup.find_all('url'):
            loc = url.find('loc').text.strip() if url.find('loc') else None
            lastmod = url.find('lastmod').text.strip() if url.find('lastmod') else None
            if loc:
                urls.append((loc, lastmod))
        logging.info(f"Found {len(urls)} URL(s) in sitemap")
        return urls, False
    else:
        logging.warning(f"Unrecognized sitemap format for {sitemap_url}")
        return [], False

def dedupe_urls(url_list):
    logging.info("Deduplicating URLs")
    unique_urls = {}
    for url, lastmod, sitemap in url_list:
        if url not in unique_urls or (lastmod and unique_urls[url]['lastmod'] > lastmod):
            unique_urls[url] = {'lastmod': lastmod, 'sitemap': sitemap}
    logging.info(f"Deduplication complete, {len(unique_urls)} unique URLs remaining")
    return unique_urls

def get_post_title(url):
    try:
        logging.debug(f"Fetching post title from {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            logging.debug(f"Successfully fetched title: {title}")
            return title.strip()
        else:
            logging.debug(f"Failed to fetch URL {url}, status code: {response.status_code}")
            return 'Failed to Retrieve'
    except requests.RequestException as e:
        logging.debug(f"Exception occurred while fetching title for {url}: {e}")
        return 'Failed to Retrieve'

def save_to_json(posts, output_filename='sitemap_posts.json'):
    logging.info(f"Saving results to {output_filename}")
    try:
        with open(output_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(posts, jsonfile, indent=4)
        logging.info(f"JSON saved successfully with {len(posts)} post(s)")
    except IOError as e:
        logging.error(f"Failed to save JSON to {output_filename}: {e}")

def parse_lastmod(lastmod_str):
    if lastmod_str is None:
        logging.warning(f"Lastmod is None, assigning a default date.")
        return datetime.min.replace(tzinfo=timezone.utc)

    formats = [
        '%Y-%m-%dT%H:%M:%S%z',  # Full ISO 8601 format with timezone
        '%Y-%m-%dT%H:%M:%S',    # ISO 8601 without timezone
        '%Y-%m-%d'              # Simple date format
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(lastmod_str, fmt)
            logging.debug(f"Parsed '{lastmod_str}' using format '{fmt}'")
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except ValueError:
            continue
    
    logging.warning(f"Failed to parse lastmod date: {lastmod_str}")
    return None

def compare_dates(lastmod_parsed, lastmod_min):
    if lastmod_parsed.tzinfo is None:
        lastmod_min_naive = lastmod_min.replace(tzinfo=None)
        return lastmod_parsed >= lastmod_min_naive
    return lastmod_parsed >= lastmod_min

def check_url_status(url):
    try:
        logging.debug(f"Checking status for URL: {url}")
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 404:
            logging.info(f"URL {url} returned 404. Excluding from results.")
            return False
        return True
    except requests.RequestException as e:
        logging.warning(f"Error checking URL {url}: {e}. Including by default.")
        return True

def sitemap2posts(blog_url, output_filename, lastmod_min, ignore_paths=None, ignore_sitemaps=None, remove_404_records=False):
    logging.info(f"Starting sitemap crawl for {blog_url}")
    
    # Step 1: Ensure only URLs starting with the base blog URL are kept.
    def url_matches_base(url):
        return url.startswith(blog_url)

    sitemaps = get_sitemaps_from_robots(blog_url)
    
    if not sitemaps:
        logging.error("No sitemaps are defined in this website's robots.txt file, so it cannot be crawled.")
        return
    
    all_urls = []
    
    for sitemap in sitemaps:
        if ignore_sitemaps and sitemap in ignore_sitemaps:
            logging.info(f"Skipping sitemap {sitemap} as per ignore_sitemaps")
            continue

        urls, is_sitemap_index = get_sitemap_urls(sitemap)
        
        if is_sitemap_index:
            for sub_sitemap in urls:
                if ignore_sitemaps and sub_sitemap in ignore_sitemaps:
                    logging.info(f"Skipping sitemap {sub_sitemap} as per ignore_sitemaps")
                    continue

                sub_urls, _ = get_sitemap_urls(sub_sitemap)
                all_urls.extend([(url, lastmod, sub_sitemap) for url, lastmod in sub_urls])
        else:
            all_urls.extend([(url, lastmod, sitemap) for url, lastmod in urls])
    
    # Deduplicate URLs (keeping the original sitemap they came from)
    deduped_urls = dedupe_urls([(url, lastmod, sitemap) for url, lastmod, sitemap in all_urls])
    
    # Filter URLs by lastmod_min and base URL
    filtered_urls = {}
    if lastmod_min:
        logging.info(f"Filtering URLs with lastmod on or after {lastmod_min.date()}")
        for url, data in deduped_urls.items():
            if url_matches_base(url):
                if data['lastmod']:
                    parsed_lastmod = parse_lastmod(data['lastmod'])
                    if parsed_lastmod and compare_dates(parsed_lastmod, lastmod_min):
                        filtered_urls[url] = data
    else:
        filtered_urls = {url: data for url, data in deduped_urls.items() if url_matches_base(url)}
    
    # Apply --ignore_domain_paths filter
    if ignore_paths:
        logging.info("Applying --ignore_domain_paths filter")
        filtered_urls = {
            url: data for url, data in filtered_urls.items()
            if not any(url.startswith(path) for path in ignore_paths)
        }
        logging.info(f"{len(filtered_urls)} URL(s) remain after applying --ignore_domain_paths filter")
    
    # Apply --remove_404_records flag
    if remove_404_records:
        logging.info("Applying --remove_404_records filter")
        valid_urls = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(check_url_status, url): url for url in filtered_urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    is_valid = future.result()
                    if is_valid:
                        valid_urls[url] = filtered_urls[url]
                except Exception as e:
                    logging.warning(f"Exception occurred while checking URL {url}: {e}")
        filtered_urls = valid_urls
        logging.info(f"{len(filtered_urls)} URL(s) remain after applying --remove_404_records filter")
    
    if not filtered_urls:
        logging.warning("No URLs to process after applying filters.")
        return
    
    # Retrieve post titles and prepare final output
    posts = []
    logging.info("Fetching post titles...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_post_title, url): url for url in filtered_urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                title = future.result()
                posts.append({
                    'url': url,
                    'lastmod': filtered_urls[url]['lastmod'],
                    'title': title,
                    'sitemap': filtered_urls[url]['sitemap']
                })
            except Exception as e:
                logging.error(f"Error fetching title for URL {url}: {e}")
    
    if not posts:
        logging.warning("No posts to save after fetching titles.")
        return
    
    # Sort posts by sitemap first, and then by lastmod (newest first)
    sorted_posts = sorted(posts, key=lambda x: (x['sitemap'], parse_lastmod(x['lastmod'])), reverse=True)
    
    # Save to JSON
    save_to_json(sorted_posts, output_filename)
    logging.info("Sitemap crawling completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve blog posts from sitemap.")
    parser.add_argument('blog_url', type=str, help='The base URL of the blog to crawl (e.g. https://www.example.com/blog/)')
    parser.add_argument('--output', type=str, default='sitemap_posts.json', help='Output JSON file name (default: sitemap_posts.json)')
    parser.add_argument('--lastmod_min', type=str, help='Filter URLs with lastmod date on or after (YYYY-MM-DD)')
    parser.add_argument('--ignore_domain_paths', type=str, help='Comma-separated list of paths to ignore, e.g., /blog/author,/blog/videos')
    parser.add_argument('--ignore_sitemaps', type=str, help='Comma-separated list of specific sitemap URLs to ignore')
    parser.add_argument('--remove_404_records', action='store_true', help='Exclude URLs that return a 404 status code.')
    
    args = parser.parse_args()
    
    # Parse lastmod_min date if provided
    lastmod_min = None
    if args.lastmod_min:
        try:
            lastmod_min = datetime.strptime(args.lastmod_min, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            logging.info(f"lastmod_min parsed as {lastmod_min} (UTC)")
        except ValueError:
            logging.error("Invalid date format for --lastmod_min. Use YYYY-MM-DD.")
            exit(1)
    
    # Parse ignore_domain_paths if provided
    ignore_paths = []
    if args.ignore_domain_paths:
        ignore_paths = [path.strip() for path in args.ignore_domain_paths.split(',')]
    
    # Parse ignore_sitemaps if provided
    ignore_sitemaps = []
    if args.ignore_sitemaps:
        ignore_sitemaps = [sitemap.strip() for sitemap in args.ignore_sitemaps.split(',')]
    
    # Call the function with the blog URL and other parameters from CLI input
    sitemap2posts(
        blog_url=args.blog_url,
        output_filename=args.output,
        lastmod_min=lastmod_min,
        ignore_paths=ignore_paths,
        ignore_sitemaps=ignore_sitemaps,
        remove_404_records=args.remove_404_records
    )
