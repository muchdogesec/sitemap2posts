## Examples

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
	--ignore_sitemaps https://www.crowdstrike.com/page-sitemap.xml https://www.crowdstrike.com/author-sitemap.xml \
	--path_ignore_list /blog/author /blog/videos \
	--remove_404_records \
	--output crowdstrike_blog.json
```