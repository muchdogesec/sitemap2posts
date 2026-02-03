#!/usr/bin/env python3
"""
Obstracts Feed Synchronization Tool

This script synchronizes blog posts from sitemaps to Obstracts feeds.
It reads configuration from a JSON file and uses the Obstracts API to create posts.
Supports GitHub Actions output with job summaries.
"""

import json
import os
import sys
import logging
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Optional
import requests

# Import the sitemap2posts function
from sitemap2posts import sitemap2posts

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class GitHubActionsOutput:
    """Handle GitHub Actions output formatting."""
    
    def __init__(self):
        """Initialize GitHub Actions output handler."""
        self.is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        self.summary_file = os.getenv('GITHUB_STEP_SUMMARY')
        self.summary_lines = []
    
    def add_summary(self, content: str):
        """Add content to GitHub Actions summary."""
        self.summary_lines.append(content)
    
    def write_summary(self):
        """Write summary to GitHub Actions summary file."""
        if self.is_github_actions and self.summary_file:
            try:
                with open(self.summary_file, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(self.summary_lines))
                    f.write('\n')
                logging.info("GitHub Actions summary written")
            except IOError as e:
                logging.error(f"Failed to write GitHub Actions summary: {e}")
    
    def set_output(self, name: str, value: str):
        """Set a GitHub Actions output variable."""
        if self.is_github_actions:
            # GitHub Actions now uses environment files
            github_output = os.getenv('GITHUB_OUTPUT')
            if github_output:
                try:
                    with open(github_output, 'a', encoding='utf-8') as f:
                        f.write(f"{name}={value}\n")
                except IOError as e:
                    logging.error(f"Failed to set GitHub output: {e}")


class ObstractsAPIClient:
    """Client for interacting with the Obstracts API."""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the Obstracts API client.
        
        Args:
            base_url: Base URL for the Obstracts API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'Token '+self.api_key,
            'Content-Type': 'application/json'
        })
    
    def create_posts_bulk(self, feed_id: str, profile_id: Optional[str], posts: List[Dict]) -> Optional[Dict]:
        """
        Create multiple posts in a feed using a single bulk request.
        
        Args:
            feed_id: The ID of the feed to post to
            profile_id: Optional profile ID to associate with posts
            posts: List of post dictionaries
        
        Returns:
            Job response if successful, None otherwise
        """
        endpoint = f"{self.base_url}/v1/feeds/{feed_id}/posts/"
        
        # Prepare payload
        payload = {
            "posts": posts,
            "profile_id": profile_id
        }
        
        try:
            logging.info(f"Submitting bulk post creation job for feed {feed_id} with {len(posts)} posts")
            response = self.session.post(endpoint, json=payload)
            
            if response.ok:
                job_data = response.json()
                job_id = job_data.get('job', {}).get('id') if isinstance(job_data.get('job'), dict) else job_data.get('job_id')
                logging.info(f"Successfully submitted job for feed {feed_id}, job_id: {job_id}")
                return job_data
            else:
                logging.error(
                    f"Failed to create posts for feed {feed_id}: "
                    f"Status {response.status_code}, Response: {response.text}"
                )
                return None
        except requests.RequestException as e:
            logging.error(f"Error creating posts for feed {feed_id}: {e}")
            return None
        
    def get_feed_details(self, feed_id: str) -> Optional[Dict]:
        """
        Retrieve feed details from the Obstracts API.
        
        Args:
            feed_id: The ID of the feed to retrieve
        Returns:
            Feed details dictionary if successful, None otherwise
        """
        endpoint = f"{self.base_url}/v1/feeds/{feed_id}/"
        
        try:
            response = self.session.get(endpoint)
            if response.ok:
                return response.json()
            else:
                logging.error(
                    f"Failed to retrieve feed {feed_id}: "
                    f"Status {response.status_code}, Response: {response.text}"
                )
                return None
        except requests.RequestException as e:
            logging.error(f"Error retrieving feed {feed_id}: {e}")
            return None

def load_config(config_path: str) -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to the configuration JSON file
    
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info(f"Loaded configuration from {config_path}")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)


def validate_config(config: Dict) -> bool:
    """
    Validate configuration to ensure all required fields are present.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if valid, exits with error if invalid
    """
    feeds = config.get('feeds', [])
    if not feeds:
        logging.error("No feeds found in configuration")
        return False
    
    for idx, feed in enumerate(feeds):
        feed_id = feed.get('feed_id', f'feed_{idx}')
        
        # Check for required fields
        if not feed.get('feed_id'):
            logging.error(f"Feed at index {idx}: Missing required field 'feed_id'")
            return False
        
        if not feed.get('sitemap_urls'):
            logging.error(f"Feed {feed_id}: Missing required field 'sitemap_urls'")
            return False
        
        if not feed.get('profile_id'):
            logging.error(f"Feed {feed_id}: Missing required field 'profile_id'")
            return False
    
    logging.info(f"Configuration validated successfully: {len(feeds)} feed(s)")
    return True


def save_config(config_path: str, config: Dict):
    """
    Save configuration to JSON file.
    
    Args:
        config_path: Path to the configuration JSON file
        config: Configuration dictionary to save
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        logging.info(f"Saved configuration to {config_path}")
    except IOError as e:
        logging.error(f"Failed to save configuration: {e}")


def prepare_post_data(post: Dict) -> Dict:
    """
    Prepare post data for Obstracts API.
    
    Args:
        post: Post dictionary from sitemap2posts
        profile_id: Optional profile ID to associate with the post
    
    Returns:
        Dictionary formatted for Obstracts API
    """
    pubdate = post.get('pubdate', datetime.now(timezone.utc).isoformat())
    data = {
        'link': post['url'],
        'title': post['title'],
        'pubdate': pubdate,
    }
    return data


def process_feed(
    feed_config: Dict,
    api_client: ObstractsAPIClient
) -> Dict:
    """
    Process a single feed configuration.
    
    Args:
        feed_config: Feed configuration dictionary
        api_client: Obstracts API client
    
    Returns:
        Statistics dictionary with job info
    """
    feed_id = feed_config.get('feed_id')
    sitemap_urls = feed_config.get('sitemap_urls', [])
    mode = feed_config.get('mode', 'robots')
    profile_id = feed_config.get('profile_id')
    lastmod_min = feed_config.get('lastmod_min')
    
    # Validate profile_id exists
    if not profile_id:
        logging.error(f"Feed {feed_id}: Missing required field 'profile_id'")
        return {
            'feed_id': feed_id,
            'posts_count': 0,
            'job_id': None,
            'success': False,
            'error': 'Missing required field: profile_id'
        }
    
    logging.info(f"Processing feed: {feed_id}")
    logging.info(f"Mode: {mode}, Sitemap URLs: {len(sitemap_urls)}")
    
    # Parse lastmod_min if provided
    lastmod_min_date = None
    if lastmod_min:
        try:
            lastmod_min_date = datetime.strptime(lastmod_min, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            logging.info(f"Filtering posts from {lastmod_min}")
        except ValueError:
            logging.error(f"Invalid lastmod_min format: {lastmod_min}")
    
    # Prepare URLs for sitemap2posts
    if mode == 'sitemap_urls':
        if not sitemap_urls:
            logging.error(f"Feed {feed_id}: sitemap_urls mode requires sitemap URLs")
            return {
                'feed_id': feed_id,
                'posts_count': 0,
                'job_id': None,
                'success': False,
                'error': 'No sitemap URLs provided'
            }
        # First URL should be the blog URL, rest are sitemap URLs
        urls = sitemap_urls
    else:
        # robots mode: only need the blog URL (first in sitemap_urls)
        if not sitemap_urls or len(sitemap_urls) == 0:
            logging.error(f"Feed {feed_id}: No blog URL provided")
            return {
                'feed_id': feed_id,
                'posts_count': 0,
                'job_id': None,
                'success': False,
                'error': 'No blog URL provided'
            }
        urls = [sitemap_urls[0]]
    
    # Fetch posts from sitemap
    posts = sitemap2posts(
        urls=urls,
        lastmod_min=lastmod_min_date,
        path_ignore_list=feed_config.get('path_ignore_list'),
        path_allow_list=feed_config.get('path_allow_list'),
        ignore_sitemaps=feed_config.get('ignore_sitemaps'),
        remove_404_records=feed_config.get('remove_404_records', False),
        mode=mode
    )
    
    if not posts:
        logging.warning(f"Feed {feed_id}: No posts found")
        return {
            'feed_id': feed_id,
            'posts_count': 0,
            'job_id': None,
            'success': True,
            'message': 'No posts found'
        }
    
    logging.info(f"Found {len(posts)} posts for feed {feed_id}")
    
    # Prepare posts for API (without profile_id in individual posts)
    api_posts = [prepare_post_data(post) for post in posts]
    
    # Upload posts to Obstracts as a single bulk request
    job_response = api_client.create_posts_bulk(feed_id, profile_id, api_posts)
    
    if not job_response:
        return {
            'feed_id': feed_id,
            'posts_count': len(posts),
            'job_id': None,
            'success': False,
            'error': 'Failed to submit job'
        }
    
    # Extract job ID from response
    job_id = job_response['id']
    
    return {
        'feed_id': feed_id,
        'posts_count': len(posts),
        'job_id': job_id,
        'success': True,
        'message': f'Submitted {len(posts)} posts'
    }


def sync_feeds(config_path: str):
    """
    Synchronize all feeds in the configuration file.
    
    Args:
        config_path: Path to the configuration JSON file
    """
    # Initialize GitHub Actions output
    gh_output = GitHubActionsOutput()
    
    # Load configuration
    config = load_config(config_path)
    
    # Validate configuration
    if not validate_config(config):
        error_msg = "Configuration validation failed. Please check the errors above."
        logging.error(error_msg)
        gh_output.add_summary(f"## ❌ Configuration Error\n\n{error_msg}")
        gh_output.write_summary()
        sys.exit(1)
    
    # Get API credentials from environment
    api_base_url = os.getenv('OBSTRACTS_API_BASE_URL')
    api_key = os.getenv('OBSTRACTS_API_KEY')
    
    if not api_base_url or not api_key:
        error_msg = (
            "Missing required environment variables: "
            "OBSTRACTS_API_BASE_URL and/or OBSTRACTS_API_KEY"
        )
        logging.error(error_msg)
        gh_output.add_summary(f"## ❌ Error\n\n{error_msg}")
        gh_output.write_summary()
        sys.exit(1)
    
    logging.info(f"Using Obstracts API: {api_base_url}")
    
    # Initialize API client
    api_client = ObstractsAPIClient(api_base_url, api_key)
    
    # Get feeds from config
    feeds = config.get('feeds', [])
    if not feeds:
        error_msg = "No feeds found in configuration"
        logging.error(error_msg)
        gh_output.add_summary(f"## ❌ Error\n\n{error_msg}")
        gh_output.write_summary()
        sys.exit(1)
    
    logging.info(f"Processing {len(feeds)} feed(s)")
    
    # Add GitHub Actions summary header
    gh_output.add_summary("# 🔄 Obstracts Feed Sync Report\n")
    gh_output.add_summary(f"**Sync Time:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    gh_output.add_summary(f"**Total Feeds:** {len(feeds)}\n")
    gh_output.add_summary("---\n")
    
    # Process each feed
    results = []
    total_posts = 0
    successful_feeds = 0
    failed_feeds = 0
    
    for feed_config in feeds:
        result = process_feed(feed_config, api_client)
        results.append(result)
        
        if result['success']:
            successful_feeds += 1
            total_posts += result['posts_count']
            
            # Add to GitHub Actions summary
            status_icon = "✅"
            gh_output.add_summary(f"## {status_icon} Feed: `{result['feed_id']}`\n")
            gh_output.add_summary(f"- **Posts Submitted:** {result['posts_count']}\n")
            if result.get('job_id'):
                gh_output.add_summary(f"- **Job ID:** `{result['job_id']}`\n")
            gh_output.add_summary(f"- **Message:** {result.get('message', 'Success')}\n")
            gh_output.add_summary("\n")
        else:
            failed_feeds += 1
            status_icon = "❌"
            gh_output.add_summary(f"## {status_icon} Feed: `{result['feed_id']}`\n")
            gh_output.add_summary(f"- **Status:** Failed\n")
            gh_output.add_summary(f"- **Error:** {result.get('error', 'Unknown error')}\n")
            gh_output.add_summary("\n")
    
    # Clean up: Remove lastmod_min from config (it should be retrieved from server)
    for feed_config in feeds:
        feed_config.pop('lastmod_min', None)
    
    # Save cleaned configuration
    save_config(config_path, config)
    
    # Add summary statistics
    gh_output.add_summary("---\n")
    gh_output.add_summary("## 📊 Summary\n")
    gh_output.add_summary(f"- **Total Posts Submitted:** {total_posts}\n")
    gh_output.add_summary(f"- **Successful Feeds:** {successful_feeds}/{len(feeds)}\n")
    gh_output.add_summary(f"- **Failed Feeds:** {failed_feeds}/{len(feeds)}\n")
    
    # Set GitHub Actions outputs
    gh_output.set_output('total_posts', str(total_posts))
    gh_output.set_output('successful_feeds', str(successful_feeds))
    gh_output.set_output('failed_feeds', str(failed_feeds))
    gh_output.set_output('total_feeds', str(len(feeds)))
    
    # Write GitHub Actions summary
    gh_output.write_summary()
    
    # Print summary to console
    logging.info("=" * 60)
    logging.info("SYNC COMPLETE")
    logging.info(f"Total posts submitted: {total_posts}")
    logging.info(f"Successful feeds: {successful_feeds}/{len(feeds)}")
    logging.info(f"Failed feeds: {failed_feeds}/{len(feeds)}")
    logging.info("=" * 60)
    
    # Exit with error code if any feeds failed
    if failed_feeds > 0:
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synchronize blog posts from sitemaps to Obstracts feeds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  OBSTRACTS_API_BASE_URL    Base URL for the Obstracts API
  OBSTRACTS_API_KEY         API key for authentication

Example:
  export OBSTRACTS_API_BASE_URL="https://management.obstracts.staging.signalscorps.com/obstracts_api"
  export OBSTRACTS_API_KEY="your-api-key"
  python obstracts_sync.py config.json
        """
    )
    
    parser.add_argument(
        'config',
        type=str,
        help='Path to the configuration JSON file'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run sync
    sync_feeds(args.config)


if __name__ == '__main__':
    main()
