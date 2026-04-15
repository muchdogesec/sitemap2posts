# Obstracts Feed Synchronization

This tool synchronizes blog posts from sitemaps to Obstracts feeds using the Obstracts API.

## Features

- **Individual Feed Configs**: Each feed has its own JSON configuration file
- **Organized by Category**: Configs organized in directories (`main/`, `issues/`, `examples/`)
- **Feed Discovery**: Automatic discovery of feed configs with filtering support
- **Batch Processing**: Configurable `posts_per_job` parameter for batch uploads
- **Job Completion Tracking**: Waits for jobs to complete with status monitoring
- **GitHub Actions Matrix Strategy**: Parallel processing of multiple feeds
- **GitHub Actions Support**: Automatic job summaries and outputs
- **Automatic Config Updates**: Updates `lastmod_min` after each successful sync

## Setup

### Environment Variables

Set the following environment variables:

```bash
export OBSTRACTS_API_BASE_URL="<OBSTRACTS WEB TOKEN>"
export OBSTRACTS_API_KEY="<YOUR OBSTRACTS WEB TOKEN>"
```

### Configuration Files

Feed configurations are stored as individual JSON files organized by category:

```
obstracts/config/
├── single_feed.example.json  # Example template
├── main/                     # Production feeds
│   ├── specterops.json
│   ├── expel.json
│   └── ...
├── issues/                   # Feeds with known issues
│   ├── darknet.json
│   └── securityledger.json
└── examples/                 # Example configurations
    ├── crowdstrike.json
    └── krebsonsecurity.json
```

Each configuration file represents a single feed. Example `specterops.json`:

```json
{
    "feed_id": "1ae489cf-f335-57a8-b96d-c87e1cd0eb78",
    "blog_url": "https://specterops.io/blog/",
    "sitemap_urls": [
        "https://specterops.io/post-sitemap.xml"
    ],
    "profile_id": "a8c00d89-b71e-51b7-84a6-fec3c5bdf7f6",
    "remove_404_records": true,
    "path_allow_list": [
        "https://specterops.io/blog/*"
    ],
    "path_ignore_list": [
        "https://specterops.io/blog/"
    ],
    "omit_author": true,
    "preferred_date": "P",
    "name": "SpecterOps"
}
```

## Configuration Options

Each feed configuration file supports the following options:

- **feed_id** (required): The Obstracts feed ID to post to
- **blog_url** (required): Blog URL to extract posts from
- **profile_id** (required): Profile UUID to associate with posts
- **name** (optional): Human-readable feed name (defaults to filename stem)
- **sitemap_urls** (optional): Array of sitemap URLs to crawl directly
  - If provided, automatically uses sitemap_urls mode
  - If omitted, uses robots mode (discovers sitemaps from robots.txt)
- **preferred_date** (optional, default: `"LPHM"`): Order of date sources to try for post publication date. Each character represents a date source:
  - `L` = lastmod (from sitemap `<lastmod>` tag)
  - `H` = htmldate (extracted from HTML content using htmldate library)
  - `P` = publish_date (from article metadata using newspaper3k)
  - `M` = modified_header (from HTTP `Last-Modified` header)
  - Example: `"LHPM"` tries lastmod first, falls back to htmldate, then publish_date, then modified_header
  - The extracted date is used both for `lastmod_min` filtering and as the `pubdate` in API requests
- **omit_author** (optional, default: `false`): Whether to exclude author information from posts sent to the API
- **use_date_filter** (optional, default: `true`): Whether to filter posts by date using `lastmod_min`. When set to `false`, all posts are included regardless of date
- **lastmod_min** (optional): Filter posts with date on or after this date (YYYY-MM-DD format)
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

Process a single feed:

```bash
python obstracts_sync.py obstracts/config/main/specterops.json --posts-per-job 64
```

### Options

- `CONFIG_FILE` (positional, required): Path to a single feed configuration JSON file
- `--posts-per-job` (required): Maximum number of posts to submit per job
- `--verbose` or `-v`: Enable verbose logging (DEBUG level)

### Feed Discovery

Use `discover_feeds.py` to find and filter feed configurations:

```bash
# List all feeds in main category
python obstracts/discover_feeds.py --include main --list

# Show feeds as markdown table
python obstracts/discover_feeds.py --markdown

# Generate GitHub Actions matrix (default: main and issues)
python obstracts/discover_feeds.py

# Filter specific feeds by filename stem
python obstracts/discover_feeds.py --filter specterops expel

# Generate matrix for specific categories
python obstracts/discover_feeds.py --include main
```

### Examples

```bash
# Process a single feed
python obstracts_sync.py obstracts/config/main/specterops.json --posts-per-job 64

# Process with verbose logging
python obstracts_sync.py obstracts/config/main/expel.json --posts-per-job 64 --verbose

# Process with larger batch size
python obstracts_sync.py obstracts/config/main/hunt.json --posts-per-job 128

# Discover all main feeds
python obstracts/discover_feeds.py --include main --list

# Filter and show specific feeds
python obstracts/discover_feeds.py --filter specterops expel --markdown
```

## How It Works

1. Reads a single feed configuration file
2. Fetches posts from sitemaps using the specified mode
3. Filters posts based on `lastmod_min` date (if provided, should be retrieved from Obstracts API)
4. Splits posts into batches based on `--posts-per-job` parameter
5. For each batch:
   - Sends a bulk POST request with all posts in the batch to the Obstracts API
   - Receives a job ID
   - Waits for the job to complete with automatic polling
   - Reports job status (processed/failed)
6. Removes `lastmod_min` from the configuration (should be retrieved from server for next run)
7. Saves the cleaned configuration back to the file
8. Outputs summary statistics and GitHub Actions summary (if running in GitHub Actions)

## API Details

### Bulk Post Creation with Batching

Posts are created using bulk requests with batching controlled by the required `--posts-per-job` parameter:

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

### Job Status Polling

After submitting each batch, the tool polls the job status endpoint:

```
GET {OBSTRACTS_API_BASE_URL}/v1/jobs/{job_id}/
```

Response:
```json
{
  "id": "job-uuid-here",
  "state": "processed",  // or "pending", "processing", "failed"
  "error": null
}
```

The tool waits for each batch's job to complete (state: `processed` or `failed`) before proceeding to the next batch. This ensures:
- Better error tracking and reporting
- Controlled resource usage
- Sequential processing with status visibility

## GitHub Actions Integration

The tool automatically detects when running in GitHub Actions and provides enhanced reporting.

### Workflow Architecture

The workflow uses a two-job strategy:

1. **discover-feeds**: Dynamically discovers feed configurations using `discover_feeds.py`
2. **sync-feeds**: Matrix strategy that runs one job per feed in parallel

### Workflow Features

- **Manual Trigger with Filters**: Optionally filter specific feeds by name
- **Category Selection**: Choose which categories to include (`main`, `issues`, etc.)
- **Parallel Processing**: Runs multiple feeds concurrently (configurable with `max-parallel`)
- **Batch Control**: Configurable `POSTS_PER_JOB` environment variable
- **Per-Feed Summaries**: Each matrix job generates its own summary

### Job Summary

A formatted markdown summary displayed in the Actions run, including:
- Feed name and ID
- Sync timestamp
- Number of posts found and submitted
- Batch-by-batch status table with job IDs
- Overall success/failure status

### Workflow Inputs

Manual trigger supports these inputs:

- **filter**: Space-separated feed stems to process (e.g., `"specterops expel"`)
- **include**: Space-separated categories to include (default: `"main"`)

### Example Matrix Output

The `discover-feeds` job generates a matrix like:

```json
{
  "include": [
    {
      "config_path": "obstracts/config/main/specterops.json",
      "name": "SpecterOps",
      "feed_id": "1ae489cf-f335-57a8-b96d-c87e1cd0eb78",
      "category": "main"
    },
    {
      "config_path": "obstracts/config/main/expel.json",
      "name": "Expel",
      "feed_id": "57f65a6f-fb84-5fd7-ba2b-6623322224fb",
      "category": "main"
    }
  ]
}
```

### Example Workflow

See `.github/workflows/obstracts-sync.yml` for the complete workflow that:
- Runs on a schedule (daily at 8 AM UTC)
- Supports manual triggers with filtering
- Dynamically discovers feeds
- Processes feeds in parallel using matrix strategy
- Limits to 2 concurrent jobs with `max-parallel: 2`
- Uses `POSTS_PER_JOB: 64` for batch processing

**Note:** Config files are not committed back since `lastmod_min` should be retrieved from the Obstracts API server for each run.

## Scheduling

### With Cron

For processing individual feeds:

```bash
# Process a specific feed every day at 8 AM
0 8 * * * cd /path/to/sitemap2posts && /path/to/python obstracts_sync.py obstracts/config/main/specterops.json --posts-per-job 64
```

For processing all feeds, create a wrapper script that iterates through configs.

### With GitHub Actions (Recommended)

GitHub Actions is recommended for multiple feeds as it provides:
- Parallel processing via matrix strategy
- Per-feed job summaries with detailed status
- Automatic feed discovery and filtering
- Built-in scheduling and manual triggers
- Secure secrets management
- Batch processing control with `POSTS_PER_JOB`

## Exit Codes

- `0`: Feed processed successfully (all batches completed)
- `1`: Feed failed, or configuration/environment error
