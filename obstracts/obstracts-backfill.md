The following records are taken from https://github.com/muchdogesec/awesome_threat_intel_blogs where no RSS feed exists.

Good = sitemap approach works

Bad = sitemap approach does not work

## Good (working well)

## Halcyon (`cfd04d80-e7f1-52c9-b6bf-3af60f5ff75c`)

```shell
python3 sitemap2posts.py https://www.halcyon.ai/blog/ \
    --path_allow_list 'https://www.halcyon.ai/blog/*' \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.halcyon.ai/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/halcyon_blog.json
```

## Sublime Security (`5782159d-3066-574c-8f3f-be1dd8288b65`)

```shell
python3 sitemap2posts.py https://sublime.security/blog/ \
    --path_allow_list 'https://proxied2.sublime.security/blog/*' \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://sublime.security/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/sublime_security_blog.json
```

## Iverify blog (`70dd1922-9678-5091-8ec8-22499dc4dbbf`)

```shell
python3 sitemap2posts.py https://iverify.io/blog/ \
    --path_allow_list 'https://iverify.io/blog/*' \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://iverify.io/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/iverify_blog.json
```

### Censys (`5bae04de-fe6e-513e-9a84-dae21a4b3734`)

```shell
python3 sitemap2posts.py https://censys.com/blog/ \
    --path_allow_list 'https://censys.com/blog/*' \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://censys.com/post-sitemap.xml \
    --remove_404_records \
    --output obstracts/output/censys_blog.json
```

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

### cyera (`2f8fc4c3-551b-537c-8cfe-25f1ba89ffb1`)

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

### nohackie (`655a1dc3-45ed-51ed-a0ae-c1d68b894ae0`)

```shell
python3 sitemap2posts.py https://nohackie.com/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://nohackie.com/sitemap.xml  \
    --remove_404_records \
    --output obstracts/output/nohackie_blog.json
```

### Reliaquest (`fe6671dc-af3a-5dc4-9f5a-ed09378bdd0c`)

```shell
python3 sitemap2posts.py https://reliaquest.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://reliaquest.com/sitemap.xml  \
    --remove_404_records \
    --output obstracts/output/reliaquest_blog.json
```

---

## Issues

### Security Ledger (`6169e9ce-e0e8-5651-b87f-8a068ddf58e9`)

https://github.com/muchdogesec/sitemap2posts/issues/31

```shell
python3 sitemap2posts.py https://securityledger.com/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://securityledger.com/sitemap-1.xml https://securityledger.com/sitemap-2.xml https://securityledger.com/sitemap-3.xml \
    --remove_404_records \
    --output obstracts/output/securityledger_blog.json
```
```json
        {
            "feed_id": "6169e9ce-e0e8-5651-b87f-8a068ddf58e9",
            "blog_url": "https://securityledger.com/",
            "sitemap_urls": [
                "https://securityledger.com/post-sitemap.xml",
                "https://securityledger.com/post-sitemap2.xml",
                "https://securityledger.com/post-sitemap3.xml"
            ],
            "profile_id": "a8c00d89-b71e-51b7-84a6-fec3c5bdf7f6",
            "remove_404_records": true,
            "path_allow_list": [
                "https://securityledger.com/*"
            ],
            "path_ignore_list": [
                "https://securityledger.com/"
            ],
            "omit_author": ,
            "preferred_date": ""
        },
```

### darknet (`6570f61e-62d2-5ee9-a8ec-f417200f5dc0`)

https://github.com/muchdogesec/sitemap2posts/issues/31

```shell
python3 sitemap2posts.py https://www.darknet.org.uk/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.darknet.org.uk/post-sitemap1.xml https://www.darknet.org.uk/post-sitemap2.xml https://www.darknet.org.uk/post-sitemap3.xml \
    --remove_404_records \
    --output obstracts/output/darknet_blog.json
```

```json
        {
            "feed_id": "6570f61e-62d2-5ee9-a8ec-f417200f5dc0",
            "blog_url": "https://www.darknet.org.uk/",
            "sitemap_urls": [
                "https://www.darknet.org.uk/post-sitemap1.xml",
                "https://www.darknet.org.uk/post-sitemap2.xml",
                "https://www.darknet.org.uk/post-sitemap3.xml"
            ],
            "profile_id": "a8c00d89-b71e-51b7-84a6-fec3c5bdf7f6",
            "remove_404_records": true,
            "path_allow_list": [
                "https://www.darknet.org.uk/*"
            ],
            "path_ignore_list": [
                "https://www.darknet.org.uk/"
            ],
            "omit_author": ,
            "preferred_date": ""
        },
```



### Blue Voyant

```shell
python3 sitemap2posts.py https://www.bluevoyant.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.bluevoyant.com/sitemaps-1-section-blog-1-sitemap.xml  \
    --remove_404_records \
    --output obstracts/output/bluevoyant_blog.json
```

### esentire

```shell
python3 sitemap2posts.py https://www.esentire.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.esentire.com/sitemaps-1-section-blog-1-sitemap-p1.xml https://www.esentire.com/sitemaps-1-section-blog-1-sitemap-p2.xml \
    --remove_404_records \
    --output obstracts/output/esentire_blog.json
```

error running scrip

### bitsight

```shell
python3 sitemap2posts.py https://www.bitsight.com/blog/ \
    --lastmod_min 2020-01-01 \
    --sitemap_urls https://www.bitsight.com/sitemaps/default/sitemap.xml \
    --remove_404_records \
    --output obstracts/output/bitsight_blog.json
```

After a few dozen requests, bitsight starts returning 429 making everything after fail so we get missing entries.

## Venture Beat

```shell
python3 sitemap2posts.py https://venturebeat.com/security/ \
    --path_allow_list 'https://venturebeat.com/security/*' \
    --lastmod_min 2020-01-01 \
    --remove_404_records \
    --output obstracts/output/venturebeat_blog.json
```

Too many requests errors.

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