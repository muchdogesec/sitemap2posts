### Bitsight

```shell
python3 sitemap2posts.py https://www.bitsight.com/blog \
    --lastmod_min 2020-01-01 \
    --ignore_sitemaps https://www.bitsight.com/sitemaps/groma/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/bitsight_blog.json
```

### SpectorOps

```shell
python3 sitemap2posts.py https://specterops.io/blog/ \
    --lastmod_min 2020-01-01 \
    --ignore_sitemaps https://specterops.io/page-sitemap.xml,https://specterops.io/resource-sitemap.xml,https://specterops.io/events-sitemap.xml,https://specterops.io/news-sitemap.xml,https://specterops.io/open_source_tools-sitemap.xml,https://specterops.io/podcast-sitemap.xml,https://specterops.io/category-sitemap.xml,https://specterops.io/post_tag-sitemap.xml,https://specterops.io/resource_type-sitemap.xml,https://specterops.io/event_type-sitemap.xml,https://specterops.io/event_topic-sitemap.xml,https://specterops.io/news_type-sitemap.xml,https://specterops.io/series-sitemap.xml,https://specterops.io/author-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/specterops_blog.json
```

### Expel

```shell
python3 sitemap2posts.py https://expel.com/blog/ \
    --lastmod_min 2020-01-01 \
    --ignore_sitemaps https://expel.com/page-sitemap.xml,https://expel.com/resource-sitemap.xml,https://expel.com/glossary-sitemap.xml,https://expel.com/industry-sitemap.xml,https://expel.com/segment-sitemap.xml,https://expel.com/glossary_category-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/expel_blog.json
```

### Hunt.io

```shell
python3 sitemap2posts.py https://hunt.io/blog \
    --remove_404_records \
    --output obstracts/output/hunt_io_blog.json
```

### Volexity

```shell
python3 sitemap2posts.py https://www.volexity.com/blog/ \
    --lastmod_min 2020-01-01 \
    --ignore_sitemaps https://www.volexity.com/page-sitemap.xml,https://www.volexity.com/news-press-sitemap.xml,https://www.volexity.com/product-sitemap.xml,https://www.volexity.com/team-member-sitemap.xml,https://www.volexity.com/tribe_events-sitemap.xml,https://www.volexity.com/category-sitemap.xml,https://www.volexity.com/post_tag-sitemap.xml,https://www.volexity.com/categories-sitemap.xml,https://www.volexity.com/tribe_events_cat-sitemap.xml,https://www.volexity.com/author-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/volexity_blog.json
```