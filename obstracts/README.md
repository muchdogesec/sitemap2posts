# Obstracts Feed Synchronization

This tool synchronizes blog posts from sitemaps to Obstracts feeds using the Obstracts API.

## Features

- **Bulk Post Creation**: Sends all posts for a feed in a single API request
- **Async Job Processing**: Submits jobs without waiting for completion
- **GitHub Actions Support**: Automatic job summaries and outputs
- **Automatic Config Updates**: Updates `lastmod_min` after each successful sync
- **Multiple Feed Support**: Process multiple feeds in a single run

## Setup

### Environment Variables

Set the following environment variables:

```bash
export OBSTRACTS_API_BASE_URL="https://management.obstracts.staging.signalscorps.com/obstracts_api"
export OBSTRACTS_API_KEY="your-api-key-here"
```

### Configuration File

Create a JSON configuration file (e.g., `obstracts_config.json`) with your feed configurations:

```json
{
    "feeds": [
        {
            "feed_id": "example-feed-id-1",
            "sitemap_urls": [
                "https://www.crowdstrike.com/blog/"
            ],
            "mode": "robots",
            "profile_id": "profile-uuid-here",
            "lastmod_min": "2024-01-01"
        },
        {
            "feed_id": "example-feed-id-2",
            "sitemap_urls": [
                "https://krebsonsecurity.com/",
                "https://krebsonsecurity.com/post-sitemap.xml"
            ],
            "mode": "sitemap_urls",
            "profile_id": "profile-uuid-here",
            "lastmod_min": "2024-01-01",
            "path_ignore_list": [
                "/blog/author",
                "*/tag/*",
                "*/archive"
            ],
            "path_allow_list": [
                "/blog/*",
                "*/2024/*"
            ],
            "remove_404_records": true
        }
    ]
}
```

## Configuration Options

Each feed in the configuration supports the following options:

- **feed_id** (required): The Obstracts feed ID to post to
- **sitemap_urls** (required): Array of URLs
  - For `robots` mode: Single blog URL (e.g., `["https://example.com/blog/"]`)
  - For `sitemap_urls` mode: Blog URL followed by sitemap URLs (e.g., `["https://example.com/blog/", "https://example.com/sitemap.xml"]`)
- **mode** (optional, default: `"robots"`): Either `"robots"` or `"sitemap_urls"`
- **profile_id** (optional): Profile UUID to associate with posts
- **lastmod_min** (optional): Filter posts with lastmod on or after this date (YYYY-MM-DD format)
  - Should be retrieved from the Obstracts API server unless manually set
  - This value is removed from the config file after each run
- **path_ignore_list** (optional): Array of URL path patterns to ignore. Supports glob patterns with wildcards `*`, `?`, and `[...]`
  - Examples: `["/blog/author", "*/tag/*", "https://example.com/*/archive"]`
- **path_allow_list** (optional): Array of URL path patterns to allow. Supports glob patterns. Only URLs matching these patterns will be included.
  - Examples: `["/blog/post/*", "*/2024/*"]`
- **ignore_sitemaps** (optional): Array of specific sitemap URLs to skip
- **remove_404_records** (optional, default: `false`): Whether to exclude URLs that return 404

## Usage

### Basic Usage

```bash
python obstracts_sync.py obstracts_config.json
```

### Options

- `--verbose` or `-v`: Enable verbose logging (DEBUG level)

### Examples

```bash
# Normal sync
python obstracts_sync.py obstracts_config.json

# Verbose logging
python obstracts_sync.py obstracts_config.json --verbose
```

## How It Works

1. Reads the configuration file with feed definitions
2. For each feed:
   - Fetches posts from sitemaps using the specified mode
   - Filters posts based on `lastmod_min` date (if provided, should be retrieved from Obstracts API)
   - Sends a **single bulk POST request** with all posts to the Obstracts API
   - Receives a job ID and continues to the next feed (does not wait for job completion)
3. Removes `lastmod_min` from the configuration (should be retrieved from server for next run)
4. Saves the cleaned configuration back to the file
5. Outputs summary statistics and GitHub Actions summary (if running in GitHub Actions)

## API Details

### Bulk Post Creation

Posts are created using a single bulk request:

```
POST {OBSTRACTS_API_BASE_URL}/v1/feeds/{feed_id}/posts/
```

Request payload:
```json
{
  "profile_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "posts": [
    {
      "title": "string",
      "link": "string",
      "pubdate": "2026-02-02T15:31:00.932Z",
      "author": "string",
      "categories": ["string"]
    }
  ]
}
```

Response:
```json
{
  "job": {
    "id": "job-uuid-here"
  }
}
```

The tool submits all posts in a single request and receives a job ID. It does **not** wait for the job to complete before moving to the next feed.

## GitHub Actions Integration

The tool automatically detects when running in GitHub Actions and provides:

### Job Summary

A formatted markdown summary displayed in the Actions run, including:
- Sync timestamp
- Status for each feed (✅/❌)
- Number of posts submitted per feed
- Job IDs for tracking
- Overall statistics

### Outputs

The following outputs are available for use in subsequent workflow steps:

- `total_posts`: Total number of posts submitted across all feeds
- `successful_feeds`: Number of feeds that succeeded
- `failed_feeds`: Number of feeds that failed
- `total_feeds`: Total number of feeds processed

### Example Workflow

See `.github/workflows/obstracts-sync.yml` for a complete example that:
- Runs on a schedule (daily at 2 AM)
- Can be triggered manually
- Installs dependencies
- Runs the sync

**Note:** The config file is not committed back to the repository since `lastmod_min` should be retrieved from the Obstracts API server for each run.

## Scheduling

### With Cron

```bash
# Run every day at 2 AM
0 2 * * * cd /path/to/sitemap2posts && /path/to/python obstracts_sync.py obstracts_config.json
```

### With GitHub Actions

See the workflow example above. GitHub Actions is recommended as it provides:
- Job summaries with detailed status
- Automatic config updates committed back to the repo
- Built-in scheduling and manual triggers
- Secure secrets management

## Exit Codes

- `0`: All feeds processed successfully
- `1`: One or more feeds failed, or configuration/environment error
