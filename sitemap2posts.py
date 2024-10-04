import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import re
import argparse
import logging
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_sitemaps_from_robots(url):
    logging.info(f"Fetching robots.txt from {url}")
    robots_url = urljoin(url, '/robots.txt')
    response = requests.get(robots_url)
    if response.status_code == 200:
        logging.info("Successfully fetched robots.txt")
        sitemaps = re.findall(r'Sitemap: (.*)', response.text)
        logging.info(f"Found {len(sitemaps)} sitemaps in robots.txt")
        return sitemaps
    else:
        logging.error(f"Failed to fetch robots.txt from {robots_url}, status code: {response.status_code}")
        return []

def get_sitemap_urls(sitemap_url):
    logging.info(f"Fetching sitemap from {sitemap_url}")
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch sitemap from {sitemap_url}, status code: {response.status_code}")
        return [], False
    
    soup = BeautifulSoup(response.content, 'lxml-xml')
    if soup.find('sitemapindex'):
        logging.info(f"{sitemap_url} is a sitemap index")
        sitemap_urls = [sitemap.text for sitemap in soup.find_all('loc')]
        logging.info(f"Found {len(sitemap_urls)} sitemaps in sitemap index")
        return sitemap_urls, True
    elif soup.find('urlset'):
        logging.info(f"{sitemap_url} is a URL set")
        urls = [(url.find('loc').text, url.find('lastmod').text if url.find('lastmod') else None) 
                for url in soup.find_all('url')]
        logging.info(f"Found {len(urls)} URLs in sitemap")
        return urls, False
    else:
        logging.warning(f"Unrecognized sitemap format for {sitemap_url}")
        return [], False

def dedupe_urls(url_list):
    logging.info("Deduplicating URLs")
    unique_urls = {}
    for url, lastmod in url_list:
        if url not in unique_urls or (lastmod and unique_urls[url] > lastmod):
            unique_urls[url] = lastmod
    logging.info(f"Deduplication complete, {len(unique_urls)} unique URLs remaining")
    return unique_urls

def get_post_title(url):
    try:
        logging.info(f"Fetching post title from {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            logging.info(f"Successfully fetched title: {title}")
            return title.strip()
        else:
            logging.error(f"Failed to fetch URL {url}, status code: {response.status_code}")
            return 'Failed to Retrieve'
    except requests.RequestException as e:
        logging.error(f"Exception occurred while fetching title for {url}: {e}")
        return 'Failed to Retrieve'

def save_to_json(posts, output_filename='sitemap_posts.json'):
    logging.info(f"Saving results to {output_filename}")
    with open(output_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(posts, jsonfile, indent=4)
    logging.info(f"JSON saved successfully with {len(posts)} posts")

def parse_lastmod(lastmod_str):
    """
    Tries to parse the lastmod date string. Handles different formats.
    Logs the detected format when successful.
    """
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',  # Full ISO 8601 format with timezone
        '%Y-%m-%dT%H:%M:%S',    # ISO 8601 without timezone
        '%Y-%m-%d'              # Simple date format
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(lastmod_str, fmt)
            logging.info(f"Parsed '{lastmod_str}' using format '{fmt}'")
            return parsed_date
        except ValueError:
            continue
    
    logging.warning(f"Failed to parse lastmod date: {lastmod_str}")
    return None

def compare_dates(lastmod_parsed, lastmod_min):
    """
    Compare the parsed lastmod date with lastmod_min, ensuring both are either offset-aware or offset-naive.
    """
    # If lastmod_parsed is offset-naive, convert lastmod_min to offset-naive for comparison
    if lastmod_parsed.tzinfo is None:
        lastmod_min_naive = lastmod_min.replace(tzinfo=None)
        return lastmod_parsed >= lastmod_min_naive
    # If lastmod_parsed is offset-aware, we can directly compare it with lastmod_min (which is offset-aware)
    return lastmod_parsed >= lastmod_min

def sitemap2posts(blog_url, output_filename, lastmod_min):
    logging.info(f"Starting sitemap crawl for {blog_url}")
    sitemaps = get_sitemaps_from_robots(blog_url)
    all_urls = []
    
    for sitemap in sitemaps:
        urls, is_sitemap_index = get_sitemap_urls(sitemap)
        
        if is_sitemap_index:
            # If it's a sitemap index, get the actual URLs from each sitemap
            for sub_sitemap in urls:
                sub_urls, _ = get_sitemap_urls(sub_sitemap)
                all_urls.extend([(url, lastmod, sub_sitemap) for url, lastmod in sub_urls])
        else:
            # If it's a regular sitemap
            all_urls.extend([(url, lastmod, sitemap) for url, lastmod in urls])
    
    # Deduplicate URLs
    deduped_urls = dedupe_urls([(url, lastmod) for url, lastmod, _ in all_urls])
    
    # Filter URLs by lastmod_min
    if lastmod_min:
        logging.info(f"Filtering URLs with lastmod after {lastmod_min}")
        filtered_urls = {}
        for url, lastmod in deduped_urls.items():
            if lastmod:
                parsed_lastmod = parse_lastmod(lastmod)
                if parsed_lastmod:
                    logging.info(f"Comparing parsed lastmod '{parsed_lastmod}' with lastmod_min '{lastmod_min}'")
                    if compare_dates(parsed_lastmod, lastmod_min):
                        filtered_urls[url] = lastmod
                    else:
                        logging.info(f"Skipping URL {url} because lastmod '{parsed_lastmod}' is before lastmod_min")
                else:
                    logging.warning(f"Skipping URL {url} because lastmod could not be parsed: {lastmod}")
        logging.info(f"{len(filtered_urls)} URLs remain after filtering by lastmod")
    else:
        filtered_urls = deduped_urls
    
    # Retrieve post titles and prepare final output
    posts = []
    for url, lastmod in filtered_urls.items():
        if url.startswith(blog_url):
            title = get_post_title(url)
            sitemap = next(sitemap for sitemap_url, _, sitemap in all_urls if sitemap_url == url)
            posts.append({'url': url, 'lastmod': lastmod, 'title': title, 'sitemap': sitemap})
    
    # Save to JSON
    save_to_json(posts, output_filename)
    logging.info("Sitemap crawling completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve blog posts from sitemap.")
    parser.add_argument('blog_url', type=str, help='The base URL of the blog to crawl (e.g. https://www.example.com/blog/)')
    parser.add_argument('--output', type=str, default='sitemap_posts.json', help='Output JSON file name (default: sitemap_posts.json)')
    parser.add_argument('--lastmod_min', type=str, help='Filter URLs with lastmod date after (YYYY-MM-DD)')

    args = parser.parse_args()
    
    # Parse lastmod_min date if provided
    lastmod_min = None
    if args.lastmod_min:
        try:
            # Convert lastmod_min to an offset-aware datetime in UTC
            lastmod_min = datetime.strptime(args.lastmod_min, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            logging.info(f"lastmod_min parsed as {lastmod_min} (UTC)")
        except ValueError:
            logging.error("Invalid date format for --lastmod_min. Use YYYY-MM-DD.")
            exit(1)
    
    # Call the function with the blog URL and lastmod_min from CLI input
    sitemap2posts(args.blog_url, args.output, lastmod_min)
