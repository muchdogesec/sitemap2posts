import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import re
import argparse
import logging

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

def save_to_csv(posts, output_filename='sitemap_posts.csv'):
    logging.info(f"Saving results to {output_filename}")
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['url', 'lastmod', 'title', 'sitemap']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for post in posts:
            writer.writerow(post)
    logging.info(f"CSV saved successfully with {len(posts)} posts")

def sitemap2posts(blog_url, output_filename):
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
    
    # Retrieve post titles and prepare final output
    posts = []
    for url, lastmod in deduped_urls.items():
        if url.startswith(blog_url):
            title = get_post_title(url)
            sitemap = next(sitemap for sitemap_url, _, sitemap in all_urls if sitemap_url == url)
            posts.append({'url': url, 'lastmod': lastmod, 'title': title, 'sitemap': sitemap})
    
    # Save to CSV
    save_to_csv(posts, output_filename)
    logging.info("Sitemap crawling completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve blog posts from sitemap.")
    parser.add_argument('blog_url', type=str, help='The base URL of the blog to crawl (e.g. https://www.example.com/blog/)')
    parser.add_argument('--output', type=str, default='sitemap_posts.csv', help='Output CSV file name (default: sitemap_posts.csv)')

    args = parser.parse_args()
    
    # Call the function with the blog URL from CLI input
    sitemap2posts(args.blog_url, args.output)
