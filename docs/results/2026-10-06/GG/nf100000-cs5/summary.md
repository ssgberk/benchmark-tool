# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 14:34:34 UTC
- Completed: 2026-10-06 21:45:54 UTC
- Commit: 4818dd2d1738f4f837fa5d80799b0beef5a92605

Suite: GG v1 · cell 1/2 (nf 100000, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 100000 | 5 | 1 | 41.860 | — | 41.860 | 41.860 | 41.860 | ok | 1 | — | 2388.9 | 12.8 | 1.32 | 7195.2 | 892.7 / 100008 | 30.4 |
| jekyll | ruby | 100000 | 5 | 1 | 81.439 | — | 81.439 | 81.439 | 81.439 | ok | 1 | — | 1227.9 | 6.6 | 0.99 | 2282.1 | 1117.7 / 100001 | 47.9 |
| astro | javascript | 100000 | 5 | 1 | 143.370 | — | 143.370 | 143.370 | 143.370 | ok | 1 | — | 697.5 | 3.7 | 1.78 | 6730.5 | 1042.8 / 100001 | 46.0 |
| hugo | go | 100000 | 5 | 1 | 145.502 | — | 145.502 | 145.502 | 145.502 | ok | 1 | — | 687.3 | 3.7 | 3.34 | 6983.4 | 1231.3 / 100003 | 27.4 |
| jigsaw | php | 100000 | 5 | 1 | 268.459 | — | 268.459 | 268.459 | 268.459 | ok | 1 | — | 372.5 | 2.0 | 0.93 | 3655.4 | 929.9 / 100003 | 63.1 |
| middleman | ruby | 100000 | 5 | 1 | 723.061 | — | 723.061 | 723.061 | 723.061 | ok | 1 | — | 138.3 | 0.7 | 3.00 | 2246.7 | 1002.2 / 100002 | 89.5 |
| mkdocs | python | 100000 | 5 | 1 | 813.923 | — | 813.923 | 813.923 | 813.923 | ok | 2 | — | 122.9 | 0.6 | 0.99 | 2689.7 | 904.1 / 100001 | 44.5 |
| lektor | python | 100000 | 5 | 1 | 951.365 | — | 951.365 | 951.365 | 951.365 | ok | 2 | — | 105.1 | 0.5 | 0.98 | 1143.7 | 831.4 / 100004 | 51.7 |
| pelican | python | 100000 | 5 | 1 | 1001.944 | — | 1001.944 | 1001.944 | 1001.944 | ok | 3 | — | 99.8 | 0.5 | 1.00 | 1054.1 | 744.4 / 100001 | 48.4 |
| nikola-mako | python | 100000 | 5 | 1 | 1910.110 | — | 1910.110 | 1910.110 | 1910.110 | ok | 1 | — | 52.4 | 0.3 | 0.99 | 3831.4 | 861.0 / 100025 | 57.2 |
| publish | swift | 100000 | 5 | 1 | 2399.525 | — | 2399.525 | 2399.525 | 2399.525 | ok | 1 | — | 41.7 | 0.2 | 1.01 | 2253.1 | 947.2 / 100004 | 136.5 |
| nanoc | ruby | 100000 | 5 | 1 | 3390.817 | — | 3390.817 | 3390.817 | 3390.817 | ok | 3 | — | 29.5 | 0.2 | 1.00 | 5372.1 | 1008.7 / 100001 | 46.9 |
| analog | javascript | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 70.2 |
| docfx | c# | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 52.9 |
| docusaurus | javascript | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 104.2 |
| dumi | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 85.3 |
| eleventy | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 41.3 |
| gatsby | javascript | 100000 | 5 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 175.6 |
| hakyll | haskell | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 2196.2 |
| hexo | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 41.1 |
| mdbook | rust | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 21.8 |
| metalsmith-handlebars | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 38.7 |
| metalsmith-nunjucks | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 39.1 |
| nextjs-export | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 50.2 |
| nextra | javascript | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 73.0 |
| nuxt-content | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 57.5 |
| observable-framework | javascript | 100000 | 5 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 50.4 |
| quarto | typescript | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 42.0 |
| quartz | javascript | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 278.8 |
| sphinx | python | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 47.4 |
| starlight | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 45.9 |
| sveltekit | javascript | 100000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 42.7 |
| vitepress | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 51.2 |
| vuepress | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 38.3 |
| zensical | python | 100000 | 5 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 55.3 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 41.860 | — | 41.860–41.860 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 81.439 | — | 81.439–81.439 |
| 2 | lektor | 951.365 | — | 951.365–951.365 |
| 3 | pelican | 1001.944 | — | 1001.944–1001.944 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | astro | 143.370 | — | 143.370–143.370 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 145.502 | — | 145.502–145.502 |
| 2 | mkdocs | 813.923 | — | 813.923–813.923 |
| 3 | nanoc | 3390.817 | — | 3390.817–3390.817 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 90616b2b906d

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 268.459 | — | 268.459–268.459 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | middleman | 723.061 | — | 723.061–723.061 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 2f62636d600c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nikola-mako | 1910.110 | — | 1910.110–1910.110 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | publish | 2399.525 | — | 2399.525–2399.525 |

## Caveats

- T9: oom means the generator exceeded the container memory limit, which is the same for every generator; it is an outcome, not a time.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

- analog (oom): oom
- docfx (failed): SSGBERK_VERIFY_FAIL build exited 255
- docusaurus (oom): oom
- dumi (failed): SSGBERK_VERIFY_FAIL build exited 134
- eleventy (failed): SSGBERK_VERIFY_FAIL build exited 134
- gatsby (timeout): timeout
- hakyll (failed)
- hexo (failed): SSGBERK_VERIFY_FAIL build exited 134
- mdbook (oom): oom
- metalsmith-handlebars (failed): SSGBERK_VERIFY_FAIL build exited 1
- metalsmith-nunjucks (failed): SSGBERK_VERIFY_FAIL build exited 1
- nextjs-export (failed)
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
- zensical (timeout): timeout
