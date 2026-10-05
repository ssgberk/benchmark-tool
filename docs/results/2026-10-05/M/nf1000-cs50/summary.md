# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:25:58 UTC
- Completed: 2026-10-05 14:54:44 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: M v1 · cell 2/2 (nf 1000, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 1000 | 50 | 5 | 2.052 | 0.027 | 2.041 | 2.040 | 2.100 | ok | 1 | 1.3% | 490.0 | 25.2 | 3.39 | 641.1 | 87.8 / 1004 | 30.0 |
| jekyll | ruby | 1000 | 50 | 5 | 3.001 | 0.161 | 3.016 | 2.826 | 3.172 | ok | 1 | 5.4% | 331.6 | 17.1 | 1.00 | 279.3 | 110.1 / 1001 | 46.4 |
| astro | javascript | 1000 | 50 | 5 | 5.664 | 0.099 | 5.638 | 5.568 | 5.827 | ok | 2 | 1.7% | 177.4 | 9.1 | 1.61 | 1384.6 | 102.2 / 1001 | 43.0 |
| eleventy | javascript | 1000 | 50 | 5 | 8.044 | 0.030 | 8.043 | 8.005 | 8.084 | ok | 1 | 0.4% | 124.3 | 6.4 | 1.22 | 1104.7 | 81.4 / 1001 | 36.2 |
| metalsmith-nunjucks | javascript | 1000 | 50 | 5 | 9.477 | 0.153 | 9.517 | 9.233 | 9.601 | ok | 1 | 1.6% | 105.1 | 5.4 | 1.17 | 543.6 | 87.1 / 1002 | 31.2 |
| metalsmith-handlebars | javascript | 1000 | 50 | 5 | 9.616 | 0.295 | 9.650 | 9.283 | 9.935 | ok | =2 | 3.1% | 103.6 | 5.3 | 1.14 | 543.8 | 87.1 / 1002 | 33.1 |
| hugo | go | 1000 | 50 | 5 | 9.693 | 0.144 | 9.717 | 9.485 | 9.857 | ok | =2 | 1.5% | 102.9 | 5.3 | 3.86 | 3865.4 | 114.4 / 1003 | 26.9 |
| nextjs-export | javascript | 1000 | 50 | 5 | 15.771 | 0.118 | 15.828 | 15.626 | 15.899 | ok | 1 | 0.7% | 63.2 | 3.2 | 3.09 | 1358.8 | 492.7 / 5021 | 51.3 |
| hexo | javascript | 1000 | 50 | 5 | 23.222 | 0.309 | 23.248 | 22.719 | 23.476 | ok | 4 | 1.3% | 43.0 | 2.2 | 1.34 | 3141.2 | 123.3 / 1001 | 40.8 |
| jigsaw | php | 1000 | 50 | 5 | 25.626 | 0.124 | 25.608 | 25.494 | 25.756 | ok | 5 | 0.5% | 39.1 | 2.0 | 1.00 | 152.7 | 84.6 / 1003 | 82.2 |
| middleman | ruby | 1000 | 50 | 5 | 32.384 | 1.085 | 32.023 | 31.299 | 33.895 | ok | 3 | 3.4% | 31.2 | 1.6 | 3.72 | 186.7 | 98.0 / 1002 | 78.4 |
| nanoc | ruby | 1000 | 50 | 5 | 55.589 | 1.421 | 55.106 | 54.377 | 57.744 | ok | 1 | 2.6% | 18.1 | 0.9 | 1.00 | 480.5 | 98.1 / 1001 | 45.8 |
| pelican | python | 1000 | 50 | 5 | 59.515 | 0.387 | 59.604 | 58.890 | 59.949 | ok | 1 | 0.6% | 16.8 | 0.9 | 1.00 | 117.6 | 72.2 / 1001 | 47.3 |
| mkdocs | python | 1000 | 50 | 5 | 69.263 | 2.910 | 68.969 | 64.935 | 72.709 | ok | 1 | 4.2% | 14.5 | 0.7 | 1.00 | 286.3 | 88.4 / 1001 | 41.0 |
| nikola-mako | python | 1000 | 50 | 5 | 164.745 | 14.520 | 158.161 | 156.844 | 190.638 | ok | 2 | 8.8% | 6.3 | 0.3 | 0.98 | 101.3 | 84.0 / 1025 | 51.4 |
| gatsby | javascript | 1000 | 50 | 5 | 244.086 | 8.233 | 242.236 | 235.375 | 257.597 | ok | 6 | 3.4% | 4.1 | 0.2 | 1.40 | 1106.3 | 171.3 / 2030 | 231.3 |
| vitepress | javascript | 1000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 38.5 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### M v1 · nf 1000, cs 50 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 2.041 | 1.3% | 2.040–2.100 |
| 2 | nikola-mako | 158.161 | 8.8% | 156.844–190.638 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 3.016 | 5.4% | 2.826–3.172 |
| 2 | astro | 5.638 | 1.7% | 5.568–5.827 |
| 3 | middleman | 32.023 | 3.4% | 31.299–33.895 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | eleventy | 8.043 | 0.4% | 8.005–8.084 |
| =2 | metalsmith-handlebars | 9.650 | 3.1% | 9.283–9.935 |
| =2 | hugo | 9.717 | 1.5% | 9.485–9.857 |
| 4 | hexo | 23.248 | 1.3% | 22.719–23.476 |
| 5 | jigsaw | 25.608 | 0.5% | 25.494–25.756 |
| 6 | gatsby | 242.236 | 3.4% | 235.375–257.597 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-nunjucks | 9.517 | 1.6% | 9.233–9.601 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint 583b6f736cfe

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nextjs-export | 15.828 | 0.7% | 15.626–15.899 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nanoc | 55.106 | 2.6% | 54.377–57.744 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint d5e881f61a8f

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 59.604 | 0.6% | 58.890–59.949 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint 90616b2b906d

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mkdocs | 68.969 | 4.2% | 64.935–72.709 |

## Failed / timeout / oom / nonconformant / unsupported

- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
