# sitemap2posts

## Overview

We use [history4feed](https://github.com/muchdogesec/history4feed) to create an archive of blogs.

This uses Wayback Machine to identify old RSS and ATOM feed URLs.

However, it is far from perfect. Sometimes WBM archives miss time periods, or simply don't index blogs at all (especially a problem with newer or niche blogs -- which account for a lot of them in the cyber-security world).

history4feed supports the ability to add posts in a feed manually to help solve this problem. However, this still requires you to get a list of missing posts.

sitemap2posts is designed to identify all posts for a blog, using sitemaps. It can automatically discover sitemaps from robots.txt or accept explicit sitemap URLs. The tool extracts all post URLs, titles, and published dates (using sitemap `lastmod` dates), and outputs them in a JSON document format that can be used with history4feed or synchronized directly to Obstracts feeds.

## Features

- **Two modes of operation:**
  - `robots` mode: Automatically discovers sitemaps from robots.txt
  - `sitemap_urls` mode: Directly specify sitemap URLs to crawl
- **Advanced filtering:**
  - Date-based filtering with `--lastmod_min`
  - Path-based filtering with glob pattern support (`--path_ignore_list`, `--path_allow_list`)
  - Sitemap exclusion (`--ignore_sitemaps`)
  - Automatic 404 detection and removal (`--remove_404_records`)
- **Obstracts Integration:**
  - Direct synchronization to Obstracts feeds via API
  - Bulk post creation with job-based processing
  - GitHub Actions support with automated summaries
- **Performance optimizations:**
  - Parallel title fetching with ThreadPoolExecutor
  - Combined 404 checking with title fetch (no duplicate requests)
  - Efficient URL deduplication

## Install

```shell
# clone the latest code
git clone https://github.com/muchdogesec/sitemap2posts
# create a venv
cd sitemap2posts
python3 -m venv sitemap2posts-venv
source sitemap2posts-venv/bin/activate
# install requirements
pip3 install -r requirements.txt
```

## Usage

### Basic Usage (robots mode)

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--output crowdstrike_blog.json
```

### With Date Filtering

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--lastmod_min 2024-01-01 \
	--output crowdstrike_blog.json
```

### With Path Filtering (Glob Patterns)

```shell
# Ignore specific paths
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--path_ignore_list /blog/author '*/tag/*' \
	--output crowdstrike_blog.json

# Only allow specific paths
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--path_allow_list '/blog/*/2024/*' '/blog/*/2025/*' \
	--output crowdstrike_blog.json

# Combine allow and ignore lists
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--path_allow_list '/blog/*' \
	--path_ignore_list /blog/author '*/tag/*' \
	--output crowdstrike_blog.json
```

### sitemap_urls Mode (Direct Sitemap URLs)

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--sitemap_urls https://www.crowdstrike.com/post-sitemap.xml https://www.crowdstrike.com/post-sitemap2.xml \
	--output crowdstrike_blog.json
```

### Complete Example with All Filters

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--lastmod_min 2024-01-01 \
	--ignore_sitemaps https://www.crowdstrike.com/page-sitemap.xml,https://www.crowdstrike.com/author-sitemap.xml \
	--path_ignore_list /blog/author /blog/videos \
	--remove_404_records \
	--output crowdstrike_blog.json
```

## Command-Line Options

* **`blog_url`** (positional): Blog URL to extract posts from
* **`--sitemap_urls`**: One or more sitemap URLs to crawl directly (automatically uses sitemap_urls mode instead of robots mode)
* **`--output`**: Output JSON file name (default: `sitemap_posts.json`)
* **`--lastmod_min`**: Filter URLs with lastmod date on or after this date (format: `YYYY-MM-DD`)
* **`--path_ignore_list`**: Path patterns to ignore. Supports glob patterns (`*`, `?`, `[...]`). Examples: `/blog/author`, `*/tag/*`, `https://example.com/*/archive`
* **`--path_allow_list`**: Path patterns to allow. Supports glob patterns. Only URLs matching these patterns will be included. Examples: `/blog/post/*`, `*/2024/*`
* **`--ignore_sitemaps`**: Comma-separated list of specific sitemap URLs to ignore
* **`--remove_404_records`**: Exclude URLs that return a 404 status code (checked during title fetch to avoid duplicate requests)

## Obstracts Integration

sitemap2posts includes `obstracts_sync.py` for direct synchronization to Obstracts feeds. See [obstracts/README.md](obstracts/README.md) for detailed documentation.

### Quick Start

```shell
# Set environment variables
export OBSTRACTS_API_BASE_URL="https://management.obstracts.staging.signalscorps.com/obstracts_api"
export OBSTRACTS_API_KEY="your-api-key"

# Run sync
python obstracts_sync.py obstracts/obstracts_config.json
```

Features:
- Bulk post creation (all posts sent in single API request per feed)
- Async job processing (doesn't wait for completion)
- GitHub Actions integration with automated summaries
- Multiple feed support with configuration file

## Examples

We keep a history of all URLs for blogs we track in our [Awesome Threat Intel Blog list](https://github.com/muchdogesec/awesome_threat_intel_blogs).

See the `examples/` directory for sample commands and outputs.

## How it works 

### Step 1: User enters URL

A user enters the base URL of a blog. e.g. `https://www.crowdstrike.com/blog/`

Note, the URL entered is important, as the sitemap entries will be filtered by sitemap2posts to only consider those that start with the url entered.

e.g. using the above example, `https://www.crowdstrike.com/blog/post.html` will be outputted, `https://www.crowdstrike.com/post.html` will not.

### Step 2: Script grabs sitemap

To do this the script hits the `robot.txt` file of the root URL.

e.g. `https://www.crowdstrike.com/robot.txt`

This can return one or more `Sitemap` entries.

```txt
User-agent: *
Sitemap: https://www.crowdstrike.com/sitemap_index.xml
Sitemap: https://www.crowdstrike.com/blog/sitemap_index.xml
Sitemap: https://www.crowdstrike.com/falcon-sitemap.xml
```

### Step 3: Script crawls all URLs in the sitemaps

The script then opens each sitemap file listed in robots.txt

This can point to a sitemap directl (e.g. `https://0xtoxin.github.io/robots.txt`)

```xml
<?xml version="1.0" encoding="UTF-8"?>

<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>http://www.example.com/</loc>
    <lastmod>2024-10-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  
  <url>
    <loc>http://www.example.com/about</loc>
    <lastmod>2024-09-25</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <url>
    <loc>http://www.example.com/contact</loc>
    <lastmod>2024-09-20</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>
```

Or a sitemap index

e.g. `https://www.crowdstrike.com/sitemap_index.xml`

```xml

<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="https://www.crowdstrike.com/wp-content/plugins/wordpress-seo/css/main-sitemap.xsl"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
	<sitemap>
		<loc>https://www.crowdstrike.com/post-sitemap.xml</loc>
		<lastmod>2024-09-26T17:20:34+00:00</lastmod>
	</sitemap>
	<sitemap>
		<loc>https://www.crowdstrike.com/post-sitemap2.xml</loc>
		<lastmod>2024-09-26T17:20:34+00:00</lastmod>
	</sitemap>
	<sitemap>
		<loc>https://www.crowdstrike.com/page-sitemap.xml</loc>
		<lastmod>2024-10-02T17:51:56+00:00</lastmod>
	</sitemap>
	<sitemap>
		<loc>https://www.crowdstrike.com/adversary-universe-sitemap.xml</loc>
		<lastmod>2024-09-27T13:57:52+00:00</lastmod>
	</sitemap>
</sitemapindex>
```

In the case of a sitemap returned, go to step 4.

If a sitemap index is returned the scripts crawls all `<loc>` urls to get the sitemap files.

### Step 4: dedupe URLs

Once all sitemap files have been identified from the robots.txt file, all `url.loc` and `url.lastmod` values are collected and stored.

The script then removes any duplicate URL entries, keeping the entry with the lowest `url.lastmod` time in such scenarios.

The list is further refined base on the `lastmod_min` time specified by the user in the command line. Here the script will remove all urls with a `lastmod` time less than that specified.

### Step 5: get post title

Finally the script should visit each URL to get the title of the post. This is a somewhat crude approach as it will grab the HTML `title`, which might not actually be exactly the same as the blog title.

### Step 6: print final file

At the last step a JSON file with `url`, `lastmod`, `title`, and `sitemap` (sitemaps url was originally found in) should be created as follows;

```json
    {
        "url": "",
        "lastmod": "",
        "title": "",
        "sitemap": ""
    }
```

#### A note on errors

In some cases sitemaps contain links that do not exist anymore (hit 404s). Occassionally the server might be down (500) or you're blocked from a page (i.e. to many requests).

In these cases, the `title` will be marked as `Failed to Retrieve`. e.g.

```json
    {
        "url": "https://www.crowdstrike.com/blog/author/vicky-ngo-lam-josh-grunzweig/",
        "lastmod": "2024-07-10T01:06:58+00:00",
        "title": "Failed to Retrieve",
        "sitemap": "https://www.crowdstrike.com/author-sitemap.xml"
    },
```

This is one reason to use the `remove_404_records` flag at script run-time.

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[Apache 2.0](/LICENSE).