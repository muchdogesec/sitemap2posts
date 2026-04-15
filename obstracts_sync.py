#!/usr/bin/env python3
"""
Obstracts Feed Synchronization Tool

This script synchronizes blog posts from a sitemap to an Obstracts feed.
It reads a single feed configuration from a JSON file and uses the Obstracts API to create posts.
Processes one feed per run - use GitHub Actions matrix for multiple feeds.
Supports GitHub Actions output with job summaries.
"""

import json
import os
import sys
import logging
import argparse
from datetime import datetime, timezone
import traceback
from typing import List, Dict, Optional
import time
import requests

# Import the sitemap2posts function
from sitemap2posts import sitemap2posts, lastmod_default

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
DEFAULT_PREFERRED_DATE = (
    "LPHM"  # Default order: Lastmod, Publish_date, Htmldate, Modified_header
)
DEFAULT_OMIT_AUTHOR = False  # Default: include author information
DEFAULT_USE_DATE_FILTER = True  # Default: filter posts by date


class GitHubActionsOutput:
    """Handle GitHub Actions output formatting."""

    def __init__(self):
        """Initialize GitHub Actions output handler."""
        self.is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
        self.summary_file = os.getenv("GITHUB_STEP_SUMMARY")
        self.summary_lines = []

    def add_summary(self, content: str):
        """Add content to GitHub Actions summary."""
        self.summary_lines.append(content)

    def write_summary(self):
        """Write summary to GitHub Actions summary file."""
        if self.is_github_actions and self.summary_file:
            try:
                with open(self.summary_file, "a", encoding="utf-8") as f:
                    f.write("\n".join(self.summary_lines))
                    f.write("\n")
                logging.info("GitHub Actions summary written")
            except IOError as e:
                logging.error(f"Failed to write GitHub Actions summary: {e}")

    def set_output(self, name: str, value: str):
        """Set a GitHub Actions output variable."""
        if self.is_github_actions:
            # GitHub Actions now uses environment files
            github_output = os.getenv("GITHUB_OUTPUT")
            if github_output:
                try:
                    with open(github_output, "a", encoding="utf-8") as f:
                        f.write(f"{name}={value}\n")
                except IOError as e:
                    logging.error(f"Failed to set GitHub output: {e}")


class JobCreationFailed(Exception):
    pass


class ObstractsAPIClient:
    """Client for interacting with the Obstracts API."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the Obstracts API client.

        Args:
            base_url: Base URL for the Obstracts API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": "Token " + self.api_key,
                "Content-Type": "application/json",
            }
        )

    def wait_for_job(
        self, job_id: str, poll_interval: int = 5, timeout: int = 300
    ) -> Dict:
        """
        Wait for a job to complete by polling its status.

        Args:
            job_id: The ID of the job to wait for
            poll_interval: Seconds between status checks (default: 5)
            timeout: Maximum time to wait in seconds (default: 300)

        Returns:
            Job details dictionary
        """
        endpoint = f"{self.base_url}/v1/jobs/{job_id}/"
        start_time = time.time()

        logging.info(f"Waiting for job {job_id} to complete...")

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                logging.error(f"Job {job_id} timed out after {timeout} seconds")
                return {
                    "id": job_id,
                    "state": "timeout",
                    "error": f"Job polling timed out after {timeout} seconds",
                }

            try:
                response = self.session.get(endpoint)
                if response.ok:
                    job_data = response.json()
                    state = job_data.get("state")
                    logging.debug(f"Job {job_id} state: {state}")

                    if state in ["processed", "failed"]:
                        logging.info(f"Job {job_id} completed with state: {state}")
                        return job_data

                    # Job is still processing
                    time.sleep(poll_interval)
                else:
                    logging.error(
                        f"Failed to get job status for {job_id}: "
                        f"Status {response.status_code}, Response: {response.text}"
                    )
                    time.sleep(poll_interval)
            except requests.RequestException as e:
                logging.error(f"Error polling job {job_id}: {e}")
                time.sleep(poll_interval)

    def create_posts_bulk(
        self,
        feed_id: str,
        profile_id: Optional[str],
        orig_posts: List[Dict],
        posts_per_job: Optional[int] = None,
    ) -> Dict:
        """
        Create multiple posts in a feed using bulk requests with optional batching.

        Args:
            feed_id: The ID of the feed to post to
            profile_id: Optional profile ID to associate with posts
            orig_posts: List of post dictionaries
            posts_per_job: Maximum number of posts per job (None = no batching)

        Returns:
            Dictionary with job results
        """
        posts = orig_posts.copy()
        total_posts = len(posts)

        # Determine batching
        if posts_per_job and posts_per_job > 0:
            logging.info(
                f"Processing {total_posts} posts for feed {feed_id} in batches of {posts_per_job}"
            )
        else:
            logging.info(
                f"Processing {total_posts} posts for feed {feed_id} in a single batch"
            )
            posts_per_job = total_posts

        # Split posts into batches
        batches = []
        for i in range(0, total_posts, posts_per_job):
            batches.append(posts[i : i + posts_per_job])

        all_jobs = []
        all_failed_posts = []
        total_submitted = 0
        batch_num = 0

        for batch in batches:
            batch_num += 1
            logging.info(
                f"Processing batch {batch_num}/{len(batches)} with {len(batch)} posts"
            )

            failed_posts = []
            job = None
            batch_posts = batch.copy()

            # Try to submit the batch (with retries)
            for retry in range(3):
                if retry:
                    logging.info(f"Retry sending posts, {retry}/2 retries")
                try:
                    job, _failed_posts = self._submit_posts(
                        feed_id, profile_id, batch_posts
                    )
                    if _failed_posts:
                        failed_posts.extend(_failed_posts)
                        all_failed_posts.extend(_failed_posts)

                    if not batch_posts:
                        # All posts already added
                        logging.info(f"Batch {batch_num}: All posts already exist")
                        all_jobs.append(
                            {
                                "batch": batch_num,
                                "job_id": "none, all posts already added",
                                "state": "skipped",
                                "posts_in_batch": len(batch),
                                "submitted": 0,
                            }
                        )
                        break

                    if job:
                        job_id = job["id"]
                        logging.info(
                            f"Batch {batch_num}: Job {job_id} created, waiting for completion..."
                        )

                        # Wait for this job to complete
                        completed_job = self.wait_for_job(job_id)

                        all_jobs.append(
                            {
                                "batch": batch_num,
                                "job_id": job_id,
                                "state": completed_job.get("state", "unknown"),
                                "posts_in_batch": len(batch),
                                "submitted": len(batch_posts),
                                "error": completed_job.get("error"),
                            }
                        )

                        total_submitted += len(batch_posts)
                        break

                except JobCreationFailed:
                    logging.error(f"Batch {batch_num}: Job creation failed")
                    break
                except Exception as e:
                    traceback.print_exc()
                    logging.error(f"Batch {batch_num}: Unexpected error: {e}")
                    continue
            else:
                # All retries failed
                all_jobs.append(
                    {
                        "batch": batch_num,
                        "job_id": None,
                        "state": "failed",
                        "posts_in_batch": len(batch),
                        "submitted": 0,
                        "error": "Failed to submit job after retries",
                    }
                )

        # Determine overall success
        success = all(job.get("state") in ["processed", "skipped"] for job in all_jobs)

        return {
            "feed_id": feed_id,
            "posts_count": total_posts,
            "jobs": all_jobs,
            "success": success,
            "submitted_posts": total_submitted,
            "failed_posts": all_failed_posts,
        }

    def _submit_posts(
        self, feed_id: str, profile_id: Optional[str], posts: List[Dict]
    ) -> tuple[Optional[Dict], list[Dict]]:
        endpoint = f"{self.base_url}/v1/feeds/{feed_id}/posts/"

        # Prepare payload
        payload = {"posts": posts, "profile_id": profile_id}
        response = self.session.post(endpoint, json=payload)
        failed_posts = []

        logging.debug(f"SUBMIT POSTS RESPONSE, {response} {response.text}")

        if response.ok:
            job_data = response.json()
            job_id = job_data["id"]
            logging.info(
                f"Successfully submitted job for feed {feed_id}, job_id: {job_id}"
            )
            return job_data, None
        elif response.status_code == 400:
            logging.error(
                f"Some errors encountered while submitting posts: {response.text}"
            )
            error_data = response.json().get("details", {})
            if "posts" not in error_data:
                raise JobCreationFailed(error_data)
            for index, error in error_data["posts"].items():
                index = int(index)
                post = posts[index]
                failed_posts.append(
                    {"url": post.pop("link"), "errors": error, "meta": post}
                )
            i = 0
            while i < len(posts):
                post = posts[i]
                if "link" not in post:
                    # remove failed posts before retry
                    posts.remove(post)
                    continue
                i += 1
        return None, failed_posts

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
                data = response.json()
                return data.get("obstract_feed_metadata", data)
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
        with open(config_path, "r", encoding="utf-8") as f:
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
        config: Configuration dictionary (single feed)

    Returns:
        True if valid, exits with error if invalid
    """
    # Configuration should be a single feed object, not an array
    if "feeds" in config:
        logging.error("Configuration should contain a single feed, not a 'feeds' array")
        return False

    # Check for required fields
    if not config.get("feed_id"):
        logging.error("Missing required field 'feed_id'")
        return False

    if not config.get("blog_url"):
        logging.error("Missing required field 'blog_url'")
        return False

    if not config.get("profile_id"):
        logging.error("Missing required field 'profile_id'")
        return False

    logging.info(
        f"Configuration validated successfully for feed: {config.get('feed_id')}"
    )
    return True


def save_config(config_path: str, config: Dict):
    """
    Save configuration to JSON file.

    Args:
        config_path: Path to the configuration JSON file
        config: Configuration dictionary to save
    """
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
        logging.info(f"Saved configuration to {config_path}")
    except IOError as e:
        logging.error(f"Failed to save configuration: {e}")


def extract_date_from_post(post: Dict, preferred_date: str) -> Optional[datetime]:
    """
    Extract date from post based on preferred_date order.

    Args:
        post: Post dictionary from sitemap2posts
        preferred_date: String like 'LHPM' where:
            L = lastmod (from sitemap)
            H = htmldate (extracted from HTML content)
            P = publish_date (from article metadata)
            M = modified_header (from HTTP Last-Modified header)

    Returns:
        datetime object or None
    """
    date_map = {
        "L": "lastmod",
        "H": "htmldate",
        "P": "publish_date",
        "M": "modified_header",
    }

    for char in preferred_date.upper():
        if char not in date_map:
            continue

        field = date_map[char]
        value = post.get(field)

        if value:
            return value

    return None


def prepare_post_data(post: Dict, omit_author: bool) -> Dict:
    """
    Prepare post data for Obstracts API.

    Args:
        post: Post dictionary from sitemap2posts

    Returns:
        Dictionary formatted for Obstracts API
    """
    # Extract date using preferred_date order

    extracted_date = post["_extracted_date"] or lastmod_default
    pubdate = extracted_date.isoformat()

    data = {
        "link": post["url"],
        "title": post["title"],
        "pubdate": pubdate,
        "author": None,
    }
    if not omit_author and "authors" in post:
        data["author"] = post["authors"]
    if "tags" in post:
        data["categories"] = post["tags"]
    return data


def process_feed(
    feed_config: Dict,
    api_client: ObstractsAPIClient,
    posts_per_job: Optional[int] = None,
) -> Dict:
    """
    Process a single feed configuration.

    Args:
        feed_config: Feed configuration dictionary
        api_client: Obstracts API client

    Returns:
        Statistics dictionary with job info
    """
    feed_id = feed_config.get("feed_id")
    blog_url = feed_config.get("blog_url")
    sitemap_urls = feed_config.get("sitemap_urls", [])
    profile_id = feed_config.get("profile_id")
    lastmod_min = feed_config.get("lastmod_min")

    feed_details = api_client.get_feed_details(feed_id)  # Ensure feed exists
    if not feed_details:
        logging.error(f"Feed {feed_id}: Could not retrieve feed details from API")
        return {
            "feed_id": feed_id,
            "posts_count": 0,
            "job_id": None,
            "success": False,
            "error": "Failed to retrieve feed details from API",
        }

    # Validate required fields
    if not blog_url:
        logging.error(f"Feed {feed_id}: Missing required field 'blog_url'")
        return {
            "feed_id": feed_id,
            "posts_count": 0,
            "job_id": None,
            "success": False,
            "error": "Missing required field: blog_url",
        }

    if not profile_id:
        logging.error(f"Feed {feed_id}: Missing required field 'profile_id'")
        return {
            "feed_id": feed_id,
            "posts_count": 0,
            "job_id": None,
            "success": False,
            "error": "Missing required field: profile_id",
        }

    # Determine mode based on presence of sitemap_urls
    logging.info(f"Processing feed: {feed_id}")
    if sitemap_urls:
        logging.info(
            f"Mode: sitemap_urls, Blog URL: {blog_url}, Sitemap URLs: {len(sitemap_urls)}"
        )
    else:
        logging.info(f"Mode: robots, Blog URL: {blog_url}")

    # Parse lastmod_min if provided
    lastmod_min_date = None
    if pubdate := feed_details.get("latest_item_pubdate"):
        try:
            lastmod_min_date = datetime.fromisoformat(pubdate)
            logging.info(f"Using feed's latest_item_pubdate for filtering: {pubdate}")
        except ValueError:
            logging.error(f"Invalid latest_item_pubdate format from feed: {pubdate}")
    elif lastmod_min:
        try:
            lastmod_min_date = datetime.strptime(lastmod_min, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            logging.info(f"Filtering posts from {lastmod_min}")
        except ValueError:
            logging.error(f"Invalid lastmod_min format: {lastmod_min}")

    # Get use_date_filter configuration (default to True)
    use_date_filter = feed_config.get("use_date_filter", DEFAULT_USE_DATE_FILTER)
    if not use_date_filter:
        logging.info("Date filtering disabled for this feed")

    if not (use_date_filter or (feed_config["preferred_date"] or "").startswith("L")):
        # don't use lastmod if it's not the preferred date filter
        lastmod_min_date = None

    # Fetch posts from sitemap
    posts = sitemap2posts(
        blog_url,
        sitemap_urls=sitemap_urls,
        lastmod_min=lastmod_min_date,
        path_ignore_list=feed_config.get("path_ignore_list"),
        path_allow_list=feed_config.get("path_allow_list"),
        ignore_sitemaps=feed_config.get("ignore_sitemaps"),
        remove_404_records=feed_config.get("remove_404_records", False),
    )

    if not posts:
        logging.warning(f"Feed {feed_id}: No posts found")
        return {
            "feed_id": feed_id,
            "posts_count": 0,
            "job_id": None,
            "success": True,
            "message": "No posts found",
        }

    logging.info(f"Found {len(posts)} posts for feed {feed_id}")

    # Get preferred_date configuration (default to 'L' for lastmod only)
    preferred_date = feed_config.get("preferred_date", DEFAULT_PREFERRED_DATE)
    logging.info(f"Using preferred_date order: {preferred_date}")

    # Get omit_author configuration (default to False)
    omit_author = feed_config.get("omit_author", DEFAULT_OMIT_AUTHOR)

    # Extract dates and filter posts by lastmod_min using the extracted date
    posts_with_dates = []
    for post in posts:
        extracted_date = extract_date_from_post(post, preferred_date)

        # Apply lastmod_min filter using the extracted date (if enabled)
        if use_date_filter and lastmod_min_date and extracted_date:
            if extracted_date < lastmod_min_date:
                logging.debug(
                    f"Filtering out {post['url']}: {extracted_date.isoformat()} < {lastmod_min_date.isoformat()}"
                )
                continue

        # Store extracted date in post for prepare_post_data
        post["_extracted_date"] = extracted_date
        posts_with_dates.append(post)

    if not posts_with_dates:
        logging.warning(f"Feed {feed_id}: No posts remaining after date filtering")
        return {
            "feed_id": feed_id,
            "posts_count": 0,
            "job_id": None,
            "success": True,
            "message": "No posts remaining after date filtering",
        }

    logging.info(f"{len(posts_with_dates)} posts remaining after date filtering")

    # Prepare posts for API using the preferred_date order
    api_posts = [prepare_post_data(post, omit_author) for post in posts_with_dates]

    # Upload posts to Obstracts with optional batching
    return api_client.create_posts_bulk(feed_id, profile_id, api_posts, posts_per_job)


def sync_feeds(config_path: str, posts_per_job: Optional[int] = None):
    """
    Synchronize a single feed from the configuration file.

    Args:
        config_path: Path to the configuration JSON file (containing a single feed)
    """
    # Initialize GitHub Actions output
    gh_output = GitHubActionsOutput()

    # Load configuration
    feed_config = load_config(config_path)

    # Validate configuration
    if not validate_config(feed_config):
        error_msg = "Configuration validation failed. Please check the errors above."
        logging.error(error_msg)
        gh_output.add_summary(f"## ❌ Configuration Error\n\n{error_msg}")
        gh_output.write_summary()
        sys.exit(1)

    # Get API credentials from environment
    api_base_url = os.getenv("OBSTRACTS_API_BASE_URL")
    api_key = os.getenv("OBSTRACTS_API_KEY")

    if not api_base_url or not api_key:
        error_msg = (
            "Missing required environment variables: "
            "`OBSTRACTS_API_BASE_URL` and/or `OBSTRACTS_API_KEY`"
        )
        logging.error(error_msg)
        gh_output.add_summary(f"## ❌ Error\n\n{error_msg}")
        gh_output.write_summary()
        sys.exit(1)

    logging.info(f"Using Obstracts API: {api_base_url}")

    # Initialize API client
    api_client = ObstractsAPIClient(api_base_url, api_key)

    # Get feed_id for logging
    feed_id = feed_config.get("feed_id")
    logging.info(f"Processing feed: {feed_id}")

    feed_name = feed_config.get("name", os.path.basename(config_path))
    # Add GitHub Actions summary header
    gh_output.add_summary(f"# 🔄 Feed Sync Report: {feed_name}\n")
    gh_output.add_summary(
        f"**Sync Time:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    )
    gh_output.add_summary(f"**Feed ID:** `{feed_id}`\n")
    gh_output.add_summary("---\n")

    # Process the feed
    result = process_feed(feed_config, api_client, posts_per_job)

    total_posts = result["posts_count"]
    submitted_posts = result.get("submitted_posts", 0)

    # Add to GitHub Actions summary
    status_icon = "✅" if result["success"] else "❌"
    gh_output.add_summary(f"\n## {status_icon} Feed: `{result['feed_id']}`\n\n")
    gh_output.add_summary(f"- **Posts Found:** {result['posts_count']}\n")
    gh_output.add_summary(f"- **Posts Submitted:** {submitted_posts}\n")

    # Show error message if failed
    if not result["success"] and result.get("error"):
        gh_output.add_summary(f"- **Error:** {result.get('error')}\n")

    # Show informational message if present
    if result.get("message"):
        gh_output.add_summary(f"- **Message:** {result['message']}\n")

    # Show job details in a table
    jobs = result.get("jobs", [])
    if jobs:
        gh_output.add_summary(
            "\n"
        )  # Blank line before table for proper markdown rendering

        # Table header
        if result["success"]:
            gh_output.add_summary("| Batch | Job ID | State | Posts | Submitted |")
            gh_output.add_summary("|-------|--------|-------|-------|-----------|")
        else:
            gh_output.add_summary(
                "| Batch | Job ID | State | Posts | Submitted | Error |"
            )
            gh_output.add_summary(
                "|-------|--------|-------|-------|-----------|-------|"
            )

        # Table rows
        for job in jobs:
            job_id = job.get("job_id", "N/A")
            state = job.get("state", "unknown")
            posts_in_batch = job.get("posts_in_batch", 0)
            submitted = job.get("submitted", 0)
            batch = job.get("batch", "?")

            # Add emoji based on state
            if state == "processed":
                state_display = "✅ processed"
            elif state == "failed":
                state_display = "❌ failed"
            elif state == "skipped":
                state_display = "⏭️ skipped"
            else:
                state_display = state

            # Build row with or without error column
            if result["success"]:
                gh_output.add_summary(
                    f"| {batch} | `{job_id}` | {state_display} | {posts_in_batch} | {submitted} |"
                )
            else:
                error = job.get("error", "")
                gh_output.add_summary(
                    f"| {batch} | `{job_id}` | {state_display} | {posts_in_batch} | {submitted} | {error} |"
                )

    gh_output.add_summary("\n")

    # Clean up: Remove lastmod_min from config (it should be retrieved from server)
    feed_config.pop("lastmod_min", None)

    # Save cleaned configuration
    save_config(config_path, feed_config)

    # Add summary statistics
    gh_output.add_summary("---\n")
    gh_output.add_summary("## 📊 Summary\n")
    gh_output.add_summary(f"- **Posts Fetched:** {total_posts}\n")
    gh_output.add_summary(f"- **Posts Submitted:** {submitted_posts}\n")
    gh_output.add_summary(
        f"- **Status:** {'✅ Success' if result['success'] else '❌ Failed'}\n"
    )

    # Set GitHub Actions outputs
    gh_output.set_output("posts_found", str(total_posts))
    gh_output.set_output("posts_submitted", str(submitted_posts))
    gh_output.set_output("success", str(result["success"]).lower())
    gh_output.set_output("feed_id", feed_id)

    # Write GitHub Actions summary
    gh_output.write_summary()

    # Print summary to console
    logging.info("=" * 60)
    logging.info("SYNC COMPLETE")
    logging.info(f"Feed ID: {feed_id}")
    logging.info(f"Posts fetched: {total_posts}")
    logging.info(f"Posts submitted: {submitted_posts}")
    logging.info(f"Status: {'Success' if result['success'] else 'Failed'}")
    logging.info("=" * 60)

    # Exit with error code if feed failed
    if not result["success"]:
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synchronize blog posts from a sitemap to an Obstracts feed. Processes one feed per run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  OBSTRACTS_API_BASE_URL    Base URL for the Obstracts API
  OBSTRACTS_API_KEY         API key for authentication

Example:
  export OBSTRACTS_API_BASE_URL="https://management.obstracts.staging.signalscorps.com/obstracts_api"
  export OBSTRACTS_API_KEY="your-api-key"
  python obstracts_sync.py feed_config.json

Note: This script processes ONE feed per run. Use GitHub Actions matrix 
strategy or run multiple times with different config files to process 
multiple feeds in parallel.
        """,
    )

    parser.add_argument(
        "config",
        type=str,
        help="Path to the feed configuration JSON file (single feed)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    parser.add_argument(
        "--posts-per-job",
        type=int,
        default=None,
        help="Maximum number of posts to send per job (default: no batching, all posts in one job)",
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run sync
    sync_feeds(args.config, args.posts_per_job)


if __name__ == "__main__":
    main()
