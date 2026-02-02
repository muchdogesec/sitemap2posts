The following records are taken from https://github.com/muchdogesec/awesome_threat_intel_blogs where no RSS feed exists.

Good = sitemap approach works

Bad = sitemap approach does not work

## Good

### SpectorOps

```shell
python3 sitemap2posts.py https://specterops.io/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://specterops.io/sitemap_index.xml \
    --remove_404_records \
    --output obstracts/output/specterops_blog.json
```

### Expel

```shell
python3 sitemap2posts.py https://expel.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://expel.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/expel_blog.json
```

### Hunt.io

```shell
python3 sitemap2posts.py https://hunt.io/blog \
    --sitemap_urls https://hunt.io/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/hunt_io_blog.json
```

No modified dates.

### Volexity

```shell
python3 sitemap2posts.py https://www.volexity.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.volexity.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/volexity_blog.json
```

### esentire

```shell
python3 sitemap2posts.py https://www.esentire.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.esentire.com/sitemaps-1-section-blog-1-sitemap-p1.xml,https://www.esentire.com/sitemaps-1-section-blog-1-sitemap-p2.xml \
    --remove_404_records \
    --output obstracts/output/esentire_blog.json
```

### ZScalar

```shell
python3 sitemap2posts.py https://www.zscaler.com/blogs/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.zscaler.com/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/zscaler_blog.json
```

### zimperium

```shell
python3 sitemap2posts.py https://www.zimperium.com/blog/\
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://zimperium.com/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/zimperium_blog.json
```

### securityscorecard

```shell
python3 sitemap2posts.py https://securityscorecard.com/blog/\
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://securityscorecard.com/blog-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/securityscorecard_blog.json
```

### dragos

```shell
python3 sitemap2posts.py https://www.dragos.com/blog/ \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/dragos_blog.json
```

### bitsight

```shell
python3 sitemap2posts.py https://www.bitsight.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.bitsight.com/sitemaps/default/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/bitsight_blog.json
```

### binary defense

```shell
python3 sitemap2posts.py https://binarydefense.com/resources/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://binarydefense.com/sitemaps-1-section-resources-1-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/binarydefense_blog.json
```

### aquasec

```shell
python3 sitemap2posts.py https://www.aquasec.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.aquasec.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/aquasec_blog.json
```

### arctic wolf

```shell
python3 sitemap2posts.py https://arcticwolf.com/resources/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://arcticwolf.com/post-sitemap.xml,https://arcticwolf.com/post-sitemap2.xml,https://arcticwolf.com/post-sitemap3.xml,https://arcticwolf.com/post-sitemap4.xml \
    --remove_404_records \
    --output obstracts/output/arcticwolf_blog.json
```

---

## Issues -- unsure cause

### cyera

```shell
python3 sitemap2posts.py https://www.cyera.com/research-labs \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/cyera_blog.json
```

---

## Bad

### Validin

```shell
python3 sitemap2posts.py https://www.validin.com/blog/ \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/zimperium_blog.json
```

Sitemap is bad.

### Team Cymru

```shell
python3 sitemap2posts.py https://www.team-cymru.com/blog \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/team-cymru_blog.json
```

Sitemap is bad.

### inteleye

```shell
python3 sitemap2posts.py https://www.inteleye.io/blog\
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/inteleye_blog.json
```

No sitemap