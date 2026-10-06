# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:29:37 UTC
- Completed: 2026-10-06 00:25:14 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: G v1 · cell 2/2 (nf 10000, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| jekyll | ruby | 10000 | 50 | 3 | 11.832 | 0.093 | 11.814 | 11.750 | 11.933 | ok | 1 | 0.8% | 846.5 | 43.5 | 0.98 | 1426.0 | 1100.8 / 10001 | 53.1 |
| zola | rust | 10000 | 50 | 3 | 25.535 | 0.044 | 25.512 | 25.507 | 25.586 | ok | 1 | 0.2% | 392.0 | 20.2 | 3.50 | 6067.3 | 877.6 / 10004 | 23.5 |
| metalsmith-handlebars | javascript | 10000 | 50 | 3 | 65.529 | 0.029 | 65.537 | 65.497 | 65.554 | ok | 1 | 0.0% | 152.6 | 7.8 | 1.11 | 2343.7 | 871.0 / 10002 | 36.0 |
| metalsmith-nunjucks | javascript | 10000 | 50 | 3 | 91.452 | 0.854 | 91.530 | 90.561 | 92.265 | ok | 2 | 0.9% | 109.3 | 5.6 | 1.10 | 2301.4 | 871.0 / 10002 | 32.5 |
| hugo | go | 10000 | 50 | 3 | 101.601 | 1.048 | 101.570 | 100.570 | 102.665 | ok | 3 | 1.0% | 98.5 | 5.1 | 3.77 | 7787.7 | 1143.7 / 10003 | 23.1 |
| nextjs-export | javascript | 10000 | 50 | 3 | 121.864 | 0.109 | 121.892 | 121.745 | 121.957 | ok | 4 | 0.1% | 82.0 | 4.2 | 2.64 | 1401.8 | 4921.4 / 50021 | 48.0 |
| jigsaw | php | 10000 | 50 | 3 | 194.266 | 0.544 | 194.244 | 193.734 | 194.821 | ok | 1 | 0.3% | 51.5 | 2.6 | 0.99 | 1153.0 | 846.2 / 10003 | 66.2 |
| middleman | ruby | 10000 | 50 | 3 | 339.884 | 0.927 | 339.690 | 339.070 | 340.892 | ok | 1 | 0.3% | 29.4 | 1.5 | 3.81 | 853.1 | 980.4 / 10002 | 96.0 |
| pelican | python | 10000 | 50 | 3 | 689.631 | 4.178 | 689.855 | 685.346 | 693.693 | ok | 5 | 0.6% | 14.5 | 0.7 | 1.00 | 789.9 | 722.4 / 10001 | 46.5 |
| nanoc | ruby | 10000 | 50 | 3 | 846.091 | 14.871 | 840.495 | 834.830 | 862.949 | ok | 6 | 1.8% | 11.9 | 0.6 | 1.00 | 3489.5 | 981.0 / 10001 | 38.3 |
| mkdocs | python | 10000 | 50 | 3 | 1130.836 | 21.791 | 1142.891 | 1105.681 | 1143.936 | ok | 7 | 1.9% | 8.7 | 0.4 | 1.00 | 2551.1 | 884.2 / 10001 | 41.5 |
| nikola-mako | python | 10000 | 50 | 3 | 1768.702 | 33.469 | 1768.797 | 1735.185 | 1802.123 | ok | 8 | 1.9% | 5.7 | 0.3 | 1.00 | 448.3 | 837.8 / 10025 | 54.3 |
| gatsby | javascript | 10000 | 50 | 3 | 2103.688 | 38.587 | 2096.804 | 2069.006 | 2145.253 | ok | 9 | 1.8% | 4.8 | 0.2 | 1.37 | 4146.8 | 1702.7 / 20030 | 222.0 |
| astro | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 50.3 |
| eleventy | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 37.9 |
| hexo | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 41.8 |
| vitepress | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 45.0 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### G v1 · nf 10000, cs 50 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 11.814 | 0.8% | 11.750–11.933 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 25.512 | 0.2% | 25.507–25.586 |
| 2 | metalsmith-nunjucks | 91.530 | 0.9% | 90.561–92.265 |
| 3 | hugo | 101.570 | 1.0% | 100.570–102.665 |
| 4 | nextjs-export | 121.892 | 0.1% | 121.745–121.957 |
| 5 | pelican | 689.855 | 0.6% | 685.346–693.693 |
| 6 | nanoc | 840.495 | 1.8% | 834.830–862.949 |
| 7 | mkdocs | 1142.891 | 1.9% | 1105.681–1143.936 |
| 8 | nikola-mako | 1768.797 | 1.9% | 1735.185–1802.123 |
| 9 | gatsby | 2096.804 | 1.8% | 2069.006–2145.253 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 65.537 | 0.0% | 65.497–65.554 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 194.244 | 0.3% | 193.734–194.821 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | middleman | 339.690 | 0.3% | 339.070–340.892 |

## Failed / timeout / oom / nonconformant / unsupported

- astro (failed): SSGBERK_VERIFY_FAIL build exited 134
- eleventy (failed): SSGBERK_VERIFY_FAIL build exited 134
- hexo (failed): SSGBERK_VERIFY_FAIL build exited 134
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
