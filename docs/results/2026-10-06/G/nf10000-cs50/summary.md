# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 13:41:13 UTC
- Completed: 2026-10-06 18:07:11 UTC
- Commit: 4818dd2d1738f4f837fa5d80799b0beef5a92605

Suite: G v1 · cell 2/2 (nf 10000, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| jekyll | ruby | 10000 | 50 | 3 | 9.020 | 0.212 | 9.051 | 8.795 | 9.216 | ok | 1 | 2.4% | 1104.9 | 56.8 | 0.98 | 1409.4 | 1100.8 / 10001 | 49.0 |
| zola | rust | 10000 | 50 | 3 | 21.965 | 0.120 | 21.914 | 21.879 | 22.102 | ok | 1 | 0.5% | 456.3 | 23.5 | 3.41 | 6072.8 | 877.6 / 10004 | 27.0 |
| metalsmith-handlebars | javascript | 10000 | 50 | 3 | 89.254 | 0.029 | 89.251 | 89.226 | 89.284 | ok | 1 | 0.0% | 112.0 | 5.8 | 1.11 | 2306.1 | 871.0 / 10002 | 34.4 |
| astro | javascript | 10000 | 50 | 3 | 92.479 | 0.620 | 92.203 | 92.045 | 93.188 | ok | 2 | 0.7% | 108.5 | 5.6 | 1.87 | 5677.1 | 1022.2 / 10001 | 47.8 |
| metalsmith-nunjucks | javascript | 10000 | 50 | 3 | 94.958 | 0.351 | 94.788 | 94.724 | 95.361 | ok | 3 | 0.4% | 105.5 | 5.4 | 1.10 | 2319.2 | 871.0 / 10002 | 37.3 |
| hugo | go | 10000 | 50 | 3 | 100.441 | 0.664 | 100.248 | 99.895 | 101.179 | ok | 4 | 0.7% | 99.8 | 5.1 | 3.78 | 7565.6 | 1143.7 / 10003 | 24.8 |
| nextjs-export | javascript | 10000 | 50 | 3 | 116.771 | 0.839 | 116.542 | 116.070 | 117.700 | ok | 1 | 0.7% | 85.8 | 4.4 | 2.59 | 1363.2 | 4921.4 / 50021 | 48.8 |
| publish | swift | 10000 | 50 | 3 | 208.102 | 4.102 | 206.336 | 205.179 | 212.791 | ok | 2 | 2.0% | 48.5 | 2.5 | 1.02 | 1406.7 | 784.0 / 10004 | 129.0 |
| jigsaw | php | 10000 | 50 | 3 | 263.277 | 2.654 | 263.655 | 260.454 | 265.721 | ok | 5 | 1.0% | 37.9 | 2.0 | 1.00 | 1152.7 | 846.2 / 10003 | 103.9 |
| middleman | ruby | 10000 | 50 | 3 | 524.466 | 9.070 | 519.245 | 519.214 | 534.939 | ok | 1 | 1.7% | 19.3 | 1.0 | 3.80 | 852.6 | 980.4 / 10002 | 114.8 |
| lektor | python | 10000 | 50 | 3 | 548.115 | 4.991 | 549.618 | 542.545 | 552.181 | ok | 3 | 0.9% | 18.2 | 0.9 | 1.00 | 772.3 | 811.2 / 10004 | 47.0 |
| pelican | python | 10000 | 50 | 3 | 643.449 | 13.887 | 638.377 | 632.810 | 659.159 | ok | 1 | 2.2% | 15.7 | 0.8 | 1.00 | 790.4 | 722.4 / 10001 | 47.5 |
| nanoc | ruby | 10000 | 50 | 3 | 805.527 | 25.089 | 800.207 | 783.524 | 832.849 | ok | 4 | 3.1% | 12.5 | 0.6 | 1.00 | 3488.3 | 981.0 / 10001 | 43.2 |
| hakyll | haskell | 10000 | 50 | 3 | 866.552 | 3.230 | 865.116 | 864.289 | 870.251 | ok | 1 | 0.4% | 11.6 | 0.6 | 3.50 | 2728.2 | 963.4 / 10003 | 2347.1 |
| mkdocs | python | 10000 | 50 | 3 | 963.788 | 10.749 | 957.657 | 957.508 | 976.199 | ok | 1 | 1.1% | 10.4 | 0.5 | 1.00 | 2556.6 | 884.2 / 10001 | 44.2 |
| docfx | c# | 10000 | 50 | 3 | 1234.162 | 39.590 | 1213.640 | 1209.047 | 1279.800 | ok | 6 | 3.2% | 8.2 | 0.4 | 1.64 | 6546.9 | 884.9 / 10006 | 53.7 |
| nikola-mako | python | 10000 | 50 | 3 | 1711.234 | 1.985 | 1711.789 | 1709.031 | 1712.882 | ok | 7 | 0.1% | 5.8 | 0.3 | 1.00 | 447.8 | 837.8 / 10025 | 47.7 |
| gatsby | javascript | 10000 | 50 | 3 | 1892.776 | 11.214 | 1896.827 | 1880.100 | 1901.402 | ok | 2 | 0.6% | 5.3 | 0.3 | 1.36 | 4120.3 | 1702.7 / 20030 | 219.0 |
| analog | javascript | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 62.1 |
| docusaurus | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 109.5 |
| dumi | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 87.8 |
| eleventy | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 40.4 |
| hexo | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 38.7 |
| mdbook | rust | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 22.9 |
| nextra | javascript | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 79.2 |
| nuxt-content | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 69.1 |
| observable-framework | javascript | 10000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 46.3 |
| quarto | typescript | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 37.1 |
| quartz | javascript | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 307.5 |
| sphinx | python | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 49.0 |
| starlight | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 49.8 |
| sveltekit | javascript | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 41.0 |
| vitepress | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 43.4 |
| vuepress | javascript | 10000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 37.5 |
| zensical | python | 10000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 51.0 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### G v1 · nf 10000, cs 50 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 9.051 | 2.4% | 8.795–9.216 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 21.914 | 0.5% | 21.879–22.102 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 89.251 | 0.0% | 89.226–89.284 |
| 2 | astro | 92.203 | 0.7% | 92.045–93.188 |
| 3 | metalsmith-nunjucks | 94.788 | 0.4% | 94.724–95.361 |
| 4 | hugo | 100.248 | 0.7% | 99.895–101.179 |
| 5 | jigsaw | 263.655 | 1.0% | 260.454–265.721 |
| 6 | docfx | 1213.640 | 3.2% | 1209.047–1279.800 |
| 7 | nikola-mako | 1711.789 | 0.1% | 1709.031–1712.882 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nextjs-export | 116.542 | 0.7% | 116.070–117.700 |
| 2 | publish | 206.336 | 2.0% | 205.179–212.791 |
| 3 | lektor | 549.618 | 0.9% | 542.545–552.181 |
| 4 | nanoc | 800.207 | 3.1% | 783.524–832.849 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | middleman | 519.245 | 1.7% | 519.214–534.939 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 638.377 | 2.2% | 632.810–659.159 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint 2f62636d600c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hakyll | 865.116 | 0.4% | 864.289–870.251 |

### G v1 · nf 10000, cs 50 · profile core · fingerprint de731ab3b8a5

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mkdocs | 957.657 | 1.1% | 957.508–976.199 |
| 2 | gatsby | 1896.827 | 0.6% | 1880.100–1901.402 |

## Caveats

- T9: oom means the generator exceeded the container memory limit, which is the same for every generator; it is an outcome, not a time.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

- analog (oom): oom
- docusaurus (failed): SSGBERK_VERIFY_FAIL build exited 134
- dumi (failed): SSGBERK_VERIFY_FAIL build exited 134
- eleventy (failed): SSGBERK_VERIFY_FAIL build exited 134
- hexo (failed): SSGBERK_VERIFY_FAIL build exited 134
- mdbook (oom): oom
- nextra (oom): oom
- nuxt-content (failed): SSGBERK_VERIFY_FAIL build exited 1
- observable-framework (timeout): timeout
- quarto (oom): oom
- quartz (oom): oom
- sphinx (oom): oom
- starlight (failed): SSGBERK_VERIFY_FAIL build exited 134
- sveltekit (oom): oom
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
- vuepress (failed): SSGBERK_VERIFY_FAIL build exited 134
- zensical (oom): oom
