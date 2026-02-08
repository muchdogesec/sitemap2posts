The following records are taken from https://github.com/muchdogesec/awesome_threat_intel_blogs where no RSS feed exists.

Good = sitemap approach works

Bad = sitemap approach does not work

## Good (working well)

### SpectorOps (`1ae489cf-f335-57a8-b96d-c87e1cd0eb78`)

```shell
python3 sitemap2posts.py https://specterops.io/blog/ \
    --path_allow_list 'https://specterops.io/blog/*' \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://specterops.io/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/specterops_blog.json
```

### Expel (`57f65a6f-fb84-5fd7-ba2b-6623322224fb`)

```shell
python3 sitemap2posts.py https://expel.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://expel.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/expel_blog.json
```

### Hunt.io (`98d67329-7040-5562-b5e6-876377cf6ae2`)

```shell
python3 sitemap2posts.py https://hunt.io/blog \
    --sitemap_urls https://hunt.io/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/hunt_io_blog.json
```

No modified dates.

### Volexity (`85818f22-92ff-5c68-8dc1-a9c6d6e505ec`)

```shell
python3 sitemap2posts.py https://www.volexity.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.volexity.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/volexity_blog.json
```

### esentire (`5cb0ff18-841e-5f46-8529-ca6f41e22d0b`)

```shell
python3 sitemap2posts.py https://www.esentire.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.esentire.com/sitemaps-1-section-blog-1-sitemap-p1.xml https://www.esentire.com/sitemaps-1-section-blog-1-sitemap-p2.xml \
    --remove_404_records \
    --output obstracts/output/esentire_blog.json
```

### ZScalar (`dcb31053-0a55-5fcd-ba0e-975cdae7dce8`)

```shell
python3 sitemap2posts.py https://www.zscaler.com/blogs/security-research/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.zscaler.com/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/zscaler_blog.json
```

### dragos (`39740aa2-052e-53ca-ad1e-32d10b79cc63`)

```shell
python3 sitemap2posts.py https://www.dragos.com/blog/ \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/dragos_blog.json
```

### bitsight (`1abb8bff-c1e6-556e-b56a-7d20b47a9b06`)

```shell
python3 sitemap2posts.py https://www.bitsight.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.bitsight.com/sitemaps/default/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/bitsight_blog.json
```

### binary defense (`6a9b10fe-0158-502e-9ec2-79149fcf2ea1`)

```shell
python3 sitemap2posts.py https://binarydefense.com/resources/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://binarydefense.com/sitemaps-1-section-resources-1-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/binarydefense_blog.json
```

### zimperium (`c069b35f-90a0-534e-a445-c54d97ad0068`)

```shell
python3 sitemap2posts.py https://zimperium.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://zimperium.com/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/zimperium_blog.json
```

### cyera

```shell
python3 sitemap2posts.py https://www.cyera.com/research-labs \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/cyera_blog.json
```

(occassional 403s)

### securityscorecard (`4d944236-3671-5881-a3bd-ae37c766406f`)

```shell
python3 sitemap2posts.py https://securityscorecard.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://securityscorecard.com/blog-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/securityscorecard_blog.json
```

(occassional 403s)

### aquasec (`d38238bc-d753-5f81-9c0f-6f31a22d7d70`)

```shell
python3 sitemap2posts.py https://www.aquasec.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.aquasec.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/aquasec_blog.json
```

(occassional 403s)

### arctic wolf (`9102b220-4788-567a-bd30-8135d28fa43e`)

```shell
python3 sitemap2posts.py https://arcticwolf.com/resources/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://arcticwolf.com/post-sitemap.xml https://arcticwolf.com/post-sitemap2.xml https://arcticwolf.com/post-sitemap3.xml https://arcticwolf.com/post-sitemap4.xml \
    --remove_404_records \
    --output obstracts/output/arcticwolf_blog.json
```

(occassional 403s)

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