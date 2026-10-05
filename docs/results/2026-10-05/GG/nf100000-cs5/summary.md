# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:39:53 UTC
- Completed: 2026-10-05 19:47:26 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: GG v1 · cell 1/2 (nf 100000, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 100000 | 5 | 1 | 35.188 | — | 35.188 | 35.188 | 35.188 | ok | 1 | — | 2841.9 | 15.2 | 2.09 | 7199.6 | 892.7 / 100008 | 21.5 |
| jekyll | ruby | 100000 | 5 | 1 | 81.297 | — | 81.297 | 81.297 | 81.297 | ok | 2 | — | 1230.1 | 6.6 | 0.98 | 2271.4 | 1117.7 / 100001 | 49.7 |
| hugo | go | 100000 | 5 | 1 | 102.691 | — | 102.691 | 102.691 | 102.691 | ok | 1 | — | 973.8 | 5.2 | 2.91 | 6908.3 | 1231.3 / 100003 | 26.5 |
| jigsaw | php | 100000 | 5 | 1 | 289.262 | — | 289.262 | 289.262 | 289.262 | ok | 2 | — | 345.7 | 1.9 | 0.94 | 3655.7 | 929.9 / 100003 | 100.0 |
| middleman | ruby | 100000 | 5 | 1 | 592.429 | — | 592.429 | 592.429 | 592.429 | ok | 3 | — | 168.8 | 0.9 | 2.93 | 2254.6 | 1002.2 / 100002 | 77.9 |
| pelican | python | 100000 | 5 | 1 | 1074.147 | — | 1074.147 | 1074.147 | 1074.147 | ok | 3 | — | 93.1 | 0.5 | 1.00 | 1052.3 | 744.4 / 100001 | 44.9 |
| mkdocs | python | 100000 | 5 | 1 | 1097.210 | — | 1097.210 | 1097.210 | 1097.210 | ok | 4 | — | 91.1 | 0.5 | 1.00 | 2691.3 | 904.1 / 100001 | 46.6 |
| nikola-mako | python | 100000 | 5 | 1 | 1836.913 | — | 1836.913 | 1836.913 | 1836.913 | ok | 1 | — | 54.4 | 0.3 | 0.99 | 3828.2 | 861.0 / 100025 | 58.0 |
| nanoc | ruby | 100000 | 5 | 1 | 3260.876 | — | 3260.876 | 3260.876 | 3260.876 | ok | 5 | — | 30.7 | 0.2 | 1.00 | 5378.7 | 1008.7 / 100001 | 44.2 |
| astro | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 44.4 |
| eleventy | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 33.2 |
| gatsby | javascript | 100000 | 5 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 229.8 |
| hexo | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 44.6 |
| metalsmith-handlebars | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 34.7 |
| metalsmith-nunjucks | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 41.7 |
| nextjs-export | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 46.2 |
| vitepress | javascript | 100000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 36.6 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### GG v1 · nf 100000, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 35.188 | — | 35.188–35.188 |
| 2 | jekyll | 81.297 | — | 81.297–81.297 |
| 3 | pelican | 1074.147 | — | 1074.147–1074.147 |
| 4 | mkdocs | 1097.210 | — | 1097.210–1097.210 |
| 5 | nanoc | 3260.876 | — | 3260.876–3260.876 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 102.691 | — | 102.691–102.691 |
| 2 | jigsaw | 289.262 | — | 289.262–289.262 |
| 3 | middleman | 592.429 | — | 592.429–592.429 |

### GG v1 · nf 100000, cs 5 · profile core · fingerprint ba134637a49c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nikola-mako | 1836.913 | — | 1836.913–1836.913 |

## Failed / timeout / oom / nonconformant / unsupported

- astro (failed): SSGBERK_VERIFY_FAIL build exited 134
- eleventy (failed): SSGBERK_VERIFY_FAIL build exited 134
- gatsby (timeout): timeout
- hexo (failed): SSGBERK_VERIFY_FAIL build exited 134
- metalsmith-handlebars (failed): SSGBERK_VERIFY_FAIL build exited 1
- metalsmith-nunjucks (failed): SSGBERK_VERIFY_FAIL build exited 1
- nextjs-export (failed)
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
