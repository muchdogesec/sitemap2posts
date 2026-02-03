



## Using robots mode (default)

Fetches sitemaps automatically from robots.txt:

```shell
python sitemap2posts.py https://krebsonsecurity.com/ \
	--output krebsonsecurity_blog.json
```

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--output crowdstrike_blog.json
```

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--lastmod_min 2024-01-01 \
	--output crowdstrike_blog.json
```

## Using sitemap_urls mode

Directly specify sitemap URLs to crawl:

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	https://www.crowdstrike.com/post-sitemap.xml \
	--mode sitemap_urls \
	--output crowdstrike_blog.json
```

```shell
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	https://www.crowdstrike.com/post-sitemap.xml \
	https://www.crowdstrike.com/post-sitemap2.xml \
	--mode sitemap_urls \
	--lastmod_min 2024-01-01 \
	--output crowdstrike_blog.json
```

```shell
python sitemap2posts.py https://krebsonsecurity.com/ \
	https://krebsonsecurity.com/wp-sitemap-posts-post-1.xml \
	https://krebsonsecurity.com/wp-sitemap-posts-post-2.xml \
	--mode sitemap_urls \
	--output krebsonsecurity_blog.json
```

## Using path filters

Filter URLs using allow and ignore lists (supports glob patterns):

```shell
# Ignore specific paths
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--path_ignore_list /blog/author /blog/videos \
	--output crowdstrike_blog.json
```

```shell
# Only allow specific paths (glob patterns)
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--path_allow_list '/blog/*/2024/*' '/blog/*/2025/*' \
	--output crowdstrike_blog.json
```

```shell
# Combine allow and ignore lists
python sitemap2posts.py https://www.crowdstrike.com/blog/ \
	--path_allow_list '/blog/*' \
	--path_ignore_list '/blog/author' '*/tag/*' '*/archive' \
	--output crowdstrike_blog.json
```