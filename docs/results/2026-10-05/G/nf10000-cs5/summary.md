# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:29:28 UTC
- Completed: 2026-10-05 15:19:05 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: G v1 · cell 1/2 (nf 10000, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 10000 | 5 | 3 | 2.605 | 0.006 | 2.604 | 2.599 | 2.612 | ok | 1 | 0.2% | 3840.9 | 20.5 | 2.67 | 752.8 | 89.2 / 10004 | 27.3 |
| jekyll | ruby | 10000 | 5 | 3 | 8.255 | 0.073 | 8.248 | 8.185 | 8.331 | ok | 1 | 0.9% | 1212.4 | 6.5 | 1.00 | 324.3 | 111.7 / 10001 | 47.7 |
| hugo | go | 10000 | 5 | 3 | 12.135 | 0.039 | 12.147 | 12.091 | 12.167 | ok | 2 | 0.3% | 823.2 | 4.4 | 3.67 | 3932.8 | 123.1 / 10003 | 22.8 |
| metalsmith-nunjucks | javascript | 10000 | 5 | 3 | 12.914 | 0.004 | 12.914 | 12.911 | 12.919 | ok | 2 | 0.0% | 774.4 | 4.1 | 1.38 | 642.4 | 88.9 / 10002 | 34.4 |
| metalsmith-handlebars | javascript | 10000 | 5 | 3 | 13.676 | 0.103 | 13.699 | 13.563 | 13.766 | ok | 3 | 0.8% | 730.0 | 3.9 | 1.36 | 665.5 | 88.9 / 10002 | 34.5 |
| astro | javascript | 10000 | 5 | 3 | 14.191 | 0.224 | 14.315 | 13.933 | 14.326 | ok | 1 | 1.6% | 698.6 | 3.7 | 1.38 | 1333.1 | 104.2 / 10001 | 43.3 |
| eleventy | javascript | 10000 | 5 | 3 | 18.672 | 0.103 | 18.681 | 18.565 | 18.771 | ok | 1 | 0.6% | 535.3 | 2.9 | 1.23 | 1304.2 | 83.0 / 10001 | 34.4 |
| hexo | javascript | 10000 | 5 | 3 | 25.853 | 0.121 | 25.815 | 25.755 | 25.989 | ok | 2 | 0.5% | 387.4 | 2.1 | 1.57 | 3648.5 | 125.4 / 10001 | 48.5 |
| jigsaw | php | 10000 | 5 | 3 | 26.701 | 0.119 | 26.681 | 26.593 | 26.828 | ok | 3 | 0.4% | 374.8 | 2.0 | 0.99 | 404.7 | 93.0 / 10003 | 89.9 |
| nextjs-export | javascript | 10000 | 5 | 3 | 49.536 | 0.659 | 49.522 | 48.883 | 50.202 | ok | 1 | 1.3% | 201.9 | 1.1 | 3.01 | 1363.1 | 650.9 / 50021 | 44.9 |
| mkdocs | python | 10000 | 5 | 3 | 66.770 | 0.569 | 66.756 | 66.208 | 67.346 | ok | 1 | 0.9% | 149.8 | 0.8 | 1.00 | 296.9 | 90.4 / 10001 | 40.2 |
| pelican | python | 10000 | 5 | 3 | 83.584 | 0.613 | 83.873 | 82.880 | 83.998 | ok | 3 | 0.7% | 119.2 | 0.6 | 1.00 | 142.1 | 74.4 / 10001 | 48.5 |
| middleman | ruby | 10000 | 5 | 3 | 87.979 | 0.576 | 87.861 | 87.471 | 88.605 | ok | 4 | 0.7% | 113.8 | 0.6 | 3.07 | 316.8 | 100.2 / 10002 | 105.9 |
| nanoc | ruby | 10000 | 5 | 3 | 117.232 | 1.533 | 117.563 | 115.560 | 118.572 | ok | 4 | 1.3% | 85.1 | 0.5 | 1.00 | 631.9 | 100.8 / 10001 | 38.0 |
| nikola-mako | python | 10000 | 5 | 3 | 218.411 | 3.826 | 218.475 | 214.553 | 222.204 | ok | 5 | 1.8% | 45.8 | 0.2 | 0.98 | 440.4 | 86.3 / 10025 | 81.9 |
| gatsby | javascript | 10000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 230.3 |
| vitepress | javascript | 10000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 38.8 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### G v1 · nf 10000, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 2.604 | 0.2% | 2.599–2.612 |
| 2 | hugo | 12.147 | 0.3% | 12.091–12.167 |
| 3 | pelican | 83.873 | 0.7% | 82.880–83.998 |
| 4 | middleman | 87.861 | 0.7% | 87.471–88.605 |
| 5 | nikola-mako | 218.475 | 1.8% | 214.553–222.204 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint fe502e5b5baa

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 8.248 | 0.9% | 8.185–8.331 |
| 2 | metalsmith-nunjucks | 12.914 | 0.0% | 12.911–12.919 |
| 3 | metalsmith-handlebars | 13.699 | 0.8% | 13.563–13.766 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint fe92e3e10f7a

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | astro | 14.315 | 1.6% | 13.933–14.326 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | eleventy | 18.681 | 0.6% | 18.565–18.771 |
| 2 | hexo | 25.815 | 0.5% | 25.755–25.989 |
| 3 | jigsaw | 26.681 | 0.4% | 26.593–26.828 |
| 4 | nanoc | 117.563 | 1.3% | 115.560–118.572 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nextjs-export | 49.522 | 1.3% | 48.883–50.202 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mkdocs | 66.756 | 0.9% | 66.208–67.346 |

## Failed / timeout / oom / nonconformant / unsupported

- gatsby (failed)
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
