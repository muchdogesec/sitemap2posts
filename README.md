# sitemap2posts

## Overview

We use [history4feed](https://github.com/muchdogesec/history4feed) to create an archive of blogs.

This uses Wayback Machine to identify old RSS and ATOM feed URLs.

However, it is far from perfect. Sometimes WBM archives miss time periods, or simply don't index blogs at all (especially a problem with newer or niche blogs -- which account for a lot of them in the cyber-security world).

history4feed supports the ability to add posts in a feed manually to help solve this problem. However, this still requires you to get a list of missing posts.

sitemap2posts is designed to identify all posts for a blog, using a specified URL path, along with titles and published dates, ready to be added to history4feed manually for processing and inclusion in a feed.

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
python sitemap2posts.py https://www.crowdstrike.com/blog/ --output custom_output.csv
```

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

This can point to a sitemap that looks like this

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

The script then removes any duplicate URL entries, keeping the entry with the lowest `url.lastmod` time.

### Step 5: get post title

Finally the script should visit each URL to get the title of the post.

### Step 6: print final file

At the last step a csv file with `url`, `lastmod`, `title`, and `sitemap` (sitemaps url was found in) should be created.

## Support

[Minimal support provided via the DOGESEC community](https://community.dogesec.com/).

## License

[Apache 2.0](/LICENSE).

