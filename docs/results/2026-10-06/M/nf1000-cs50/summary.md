# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 11:16:14 UTC
- Completed: 2026-10-06 13:35:22 UTC
- Commit: 54be4010a4aabbba9c5580d321dcc52e23460537

Suite: M v1 · cell 2/2 (nf 1000, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 1000 | 50 | 5 | 2.602 | 0.017 | 2.599 | 2.582 | 2.630 | ok | 1 | 0.7% | 384.8 | 19.8 | 3.48 | 641.0 | 87.8 / 1004 | 26.5 |
| jekyll | ruby | 1000 | 50 | 5 | 3.743 | 0.039 | 3.740 | 3.703 | 3.807 | ok | 1 | 1.0% | 267.4 | 13.8 | 1.00 | 272.3 | 110.1 / 1001 | 48.5 |
| mdbook | rust | 1000 | 50 | 5 | 6.162 | 0.074 | 6.151 | 6.081 | 6.253 | ok | 1 | 1.2% | 162.6 | 8.3 | 0.99 | 1506.0 | 118.6 / 1019 | 31.1 |
| eleventy | javascript | 1000 | 50 | 5 | 6.368 | 0.032 | 6.387 | 6.316 | 6.391 | ok | 2 | 0.5% | 156.6 | 8.0 | 1.22 | 1116.6 | 81.4 / 1001 | 42.4 |
| metalsmith-handlebars | javascript | 1000 | 50 | 5 | 9.361 | 0.090 | 9.338 | 9.260 | 9.502 | ok | =2 | 1.0% | 107.1 | 5.5 | 1.13 | 551.3 | 87.1 / 1002 | 38.0 |
| astro | javascript | 1000 | 50 | 5 | 9.447 | 0.057 | 9.463 | 9.375 | 9.508 | ok | =2 | 0.6% | 105.7 | 5.4 | 1.52 | 1346.2 | 102.2 / 1001 | 46.0 |
| metalsmith-nunjucks | javascript | 1000 | 50 | 5 | 9.578 | 0.272 | 9.468 | 9.242 | 9.892 | ok | =2 | 2.8% | 105.6 | 5.4 | 1.15 | 563.4 | 87.1 / 1002 | 37.3 |
| hugo | go | 1000 | 50 | 5 | 9.754 | 0.113 | 9.791 | 9.565 | 9.855 | ok | 1 | 1.2% | 102.1 | 5.3 | 3.90 | 3899.8 | 114.4 / 1003 | 28.9 |
| hexo | javascript | 1000 | 50 | 5 | 14.718 | 0.343 | 14.909 | 14.316 | 15.066 | ok | 1 | 2.3% | 67.1 | 3.4 | 1.35 | 3438.9 | 123.3 / 1001 | 44.0 |
| nextjs-export | javascript | 1000 | 50 | 5 | 16.637 | 0.700 | 16.377 | 15.944 | 17.677 | ok | 3 | 4.2% | 61.1 | 3.1 | 2.37 | 1417.5 | 492.7 / 5021 | 64.5 |
| jigsaw | php | 1000 | 50 | 5 | 18.991 | 0.058 | 18.974 | 18.935 | 19.082 | ok | 1 | 0.3% | 52.7 | 2.7 | 1.00 | 152.9 | 84.6 / 1003 | 102.5 |
| publish | swift | 1000 | 50 | 5 | 20.168 | 0.168 | 20.272 | 19.964 | 20.317 | ok | 5 | 0.8% | 49.3 | 2.5 | 1.02 | 161.1 | 78.4 / 1004 | 133.7 |
| starlight | javascript | 1000 | 50 | 5 | 34.652 | 0.205 | 34.732 | 34.292 | 34.803 | ok | 6 | 0.6% | 28.8 | 1.5 | 1.44 | 2488.3 | 299.3 / 1014 | 46.0 |
| pelican | python | 1000 | 50 | 5 | 49.219 | 0.322 | 49.311 | 48.674 | 49.530 | ok | 1 | 0.7% | 20.3 | 1.0 | 1.00 | 117.5 | 72.2 / 1001 | 46.7 |
| middleman | ruby | 1000 | 50 | 5 | 52.090 | 0.668 | 52.168 | 51.082 | 52.956 | ok | 7 | 1.3% | 19.2 | 1.0 | 3.74 | 186.2 | 98.0 / 1002 | 100.2 |
| lektor | python | 1000 | 50 | 5 | 60.449 | 0.768 | 60.027 | 59.682 | 61.434 | ok | 1 | 1.3% | 16.7 | 0.9 | 1.00 | 153.4 | 81.1 / 1004 | 51.2 |
| nanoc | ruby | 1000 | 50 | 5 | 68.197 | 0.692 | 68.362 | 67.006 | 68.790 | ok | 2 | 1.0% | 14.6 | 0.8 | 1.00 | 480.5 | 98.1 / 1001 | 42.2 |
| hakyll | haskell | 1000 | 50 | 5 | 79.262 | 4.833 | 82.005 | 72.465 | 83.592 | ok | =4 | 6.1% | 12.2 | 0.6 | 3.44 | 2581.1 | 96.3 / 1003 | 2256.6 |
| vuepress ⚠ | javascript | 1000 | 50 | 10 | 100.508 | 15.128 | 105.719 | 58.025 | 107.836 | ok | =4 | 15.1% | 9.5 | 0.5 | 2.74 | 8373.3 | 213.1 / 2009 | 44.3 |
| mkdocs | python | 1000 | 50 | 5 | 105.132 | 0.635 | 104.820 | 104.560 | 105.949 | ok | 8 | 0.6% | 9.5 | 0.5 | 1.00 | 286.3 | 88.4 / 1001 | 48.3 |
| analog | javascript | 1000 | 50 | 5 | 108.560 | 1.908 | 108.834 | 106.304 | 110.456 | ok | 9 | 1.8% | 9.2 | 0.5 | 1.28 | 4679.4 | 191.6 / 2008 | 65.2 |
| docfx | c# | 1000 | 50 | 5 | 116.354 | 0.819 | 116.365 | 115.343 | 117.563 | ok | 10 | 0.7% | 8.6 | 0.4 | 1.69 | 877.5 | 88.5 / 1006 | 51.7 |
| nikola-mako | python | 1000 | 50 | 5 | 159.804 | 1.599 | 159.615 | 157.564 | 161.941 | ok | 6 | 1.0% | 6.3 | 0.3 | 0.97 | 102.3 | 84.0 / 1025 | 52.4 |
| gatsby | javascript | 1000 | 50 | 5 | 217.293 | 2.386 | 217.825 | 213.712 | 219.796 | ok | 1 | 1.1% | 4.6 | 0.2 | 1.42 | 1137.8 | 171.3 / 2030 | 212.4 |
| zensical | python | 1000 | 50 | 5 | 312.517 | 0.780 | 312.455 | 311.470 | 313.322 | ok | 11 | 0.2% | 3.2 | 0.2 | 1.01 | 1336.5 | 200.8 / 1014 | 58.0 |
| sveltekit | javascript | 1000 | 50 | 5 | 335.522 | 1.799 | 335.162 | 333.226 | 338.104 | ok | 7 | 0.5% | 3.0 | 0.2 | 1.46 | 4582.7 | 172.9 / 2020 | 42.2 |
| nuxt-content | javascript | 1000 | 50 | 5 | 351.168 | 8.348 | 354.676 | 336.390 | 356.406 | ok | 1 | 2.4% | 2.8 | 0.1 | 1.38 | 5981.9 | 401.8 / 2053 | 51.8 |
| observable-framework | javascript | 1000 | 50 | 5 | 586.812 | 3.984 | 585.628 | 583.030 | 591.262 | ok | 2 | 0.7% | 1.7 | 0.1 | 1.21 | 1242.9 | 110.3 / 1007 | 44.7 |
| sphinx | python | 1000 | 50 | 5 | 806.061 | 23.162 | 805.490 | 782.164 | 830.849 | ok | 12 | 2.9% | 1.2 | 0.1 | 1.00 | 7212.0 | 131.3 / 1005 | 45.7 |
| docusaurus | javascript | 1000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 109.0 |
| dumi | javascript | 1000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 77.5 |
| nextra | javascript | 1000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 71.0 |
| quarto | typescript | 1000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 37.4 |
| quartz | javascript | 1000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 197.6 |
| vitepress | javascript | 1000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 37.1 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### M v1 · nf 1000, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 2.599 | 0.7% | 2.582–2.630 |
| =2 | metalsmith-handlebars | 9.338 | 1.0% | 9.260–9.502 |
| =2 | astro | 9.463 | 0.6% | 9.375–9.508 |
| =2 | metalsmith-nunjucks | 9.468 | 2.8% | 9.242–9.892 |
| 5 | publish | 20.272 | 0.8% | 19.964–20.317 |
| 6 | starlight | 34.732 | 0.6% | 34.292–34.803 |
| 7 | middleman | 52.168 | 1.3% | 51.082–52.956 |
| 8 | mkdocs | 104.820 | 0.6% | 104.560–105.949 |
| 9 | analog | 108.834 | 1.8% | 106.304–110.456 |
| 10 | docfx | 116.365 | 0.7% | 115.343–117.563 |
| 11 | zensical | 312.455 | 0.2% | 311.470–313.322 |
| 12 | sphinx | 805.490 | 2.9% | 782.164–830.849 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 3.740 | 1.0% | 3.703–3.807 |
| 2 | eleventy | 6.387 | 0.5% | 6.316–6.391 |
| 3 | nextjs-export | 16.377 | 4.2% | 15.944–17.677 |
| =4 | hakyll | 82.005 | 6.1% | 72.465–83.592 |
| =4 | vuepress ⚠ | 105.719 | 15.1% | 58.025–107.836 |
| 6 | nikola-mako | 159.615 | 1.0% | 157.564–161.941 |
| 7 | sveltekit | 335.162 | 0.5% | 333.226–338.104 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint d5e881f61a8f

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mdbook | 6.151 | 1.2% | 6.081–6.253 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 9.791 | 1.2% | 9.565–9.855 |
| 2 | observable-framework | 585.628 | 0.7% | 583.030–591.262 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hexo | 14.909 | 2.3% | 14.316–15.066 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint e0710eca8adb

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 18.974 | 0.3% | 18.935–19.082 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint ba134637a49c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 49.311 | 0.7% | 48.674–49.530 |
| 2 | nanoc | 68.362 | 1.0% | 67.006–68.790 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint dbc7b3c4cf92

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | lektor | 60.027 | 1.3% | 59.682–61.434 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint de731ab3b8a5

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | gatsby | 217.825 | 1.1% | 213.712–219.796 |

### M v1 · nf 1000, cs 50 · profile core · fingerprint c5ccc7094d75

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nuxt-content | 354.676 | 2.4% | 336.390–356.406 |

## Caveats

- Noisy: results marked ⚠ had a CV above 10% (protocol cvThreshold) on their last attempt.
- T9: oom means the generator exceeded the container memory limit, which is the same for every generator; it is an outcome, not a time.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

- docusaurus (failed): SSGBERK_VERIFY_FAIL build exited 134
- dumi (failed): SSGBERK_VERIFY_FAIL build exited 134
- nextra (oom): oom
- quarto (timeout): timeout
- quartz (oom): oom
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
