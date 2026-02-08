# sitemap2posts

## Overview

We use [history4feed](https://github.com/muchdogesec/history4feed) to create an archive of blogs.

This uses Wayback Machine to identify old RSS and ATOM feed URLs.

However, it is far from perfect. Sometimes WBM archives miss time periods, or simply don't index blogs at all (especially a problem with newer or niche blogs -- which account for a lot of them in the cyber-security world).

history4feed supports the ability to add posts in a feed manually to help solve this problem. However, this still requires you to get a list of missing posts.

sitemap2posts is designed to identify all posts for a blog, using sitemaps. It can automatically discover sitemaps from robots.txt or accept explicit sitemap URLs. The tool extracts all post URLs, titles, and published dates (using sitemap `lastmod` dates), and outputs them in a JSON document format that can be used with history4feed or synchronized directly to Obstracts feeds.

## Features

- **Two modes of operation:**
  - `robots` mode (default): Automatically discovers sitemaps from robots.txt
  - `sitemap_urls` mode: Directly specify sitemap URLs to crawl
- **Smart data extraction**
	- Will extract title, authors and publish date from the report
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

## Run

```shell
python sitemap2posts.py BLOG_URL
```

### Command-Line Options

* **`blog_url`** (positional): Blog URL to extract posts from
* **`--sitemap_urls`**: One or more sitemap URLs to crawl directly (automatically uses sitemap_urls mode instead of robots mode)
* **`--output`**: Output JSON file name (default: `sitemap_posts.json`)
* **`--lastmod_min`**: Filter URLs with lastmod date on or after this date (format: `YYYY-MM-DD`)
* **`--path_ignore_list`**: Path patterns to ignore. Supports glob patterns (`*`, `?`, `[...]`). Examples: `/blog/author`, `*/tag/*`, `https://example.com/*/archive`
* **`--path_allow_list`**: Path patterns to allow. Supports glob patterns. Only URLs matching these patterns will be included. Examples: `/blog/post/*`, `*/2024/*`
* **`--ignore_sitemaps`**: Comma-separated list of specific sitemap URLs to ignore
* **`--remove_404_records`**: Exclude URLs that return a 404 status code (checked during title fetch to avoid duplicate requests)

### Examples

See the `examples/` directory for sample commands showing how to use this script.

## Obstracts Integration

sitemap2posts includes `obstracts_sync.py` for direct synchronization to Obstracts feeds.

See [obstracts/README.md](obstracts/README.md) for detailed documentation.

## Useful link

- [Awesome Threat Intel Blog list](https://github.com/muchdogesec/awesome_threat_intel_blogs).]

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[Apache 2.0](/LICENSE).