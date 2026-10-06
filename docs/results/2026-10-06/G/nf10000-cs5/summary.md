# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 13:41:15 UTC
- Completed: 2026-10-06 18:30:09 UTC
- Commit: 4818dd2d1738f4f837fa5d80799b0beef5a92605

Suite: G v1 · cell 1/2 (nf 10000, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 10000 | 5 | 3 | 2.085 | 0.062 | 2.103 | 2.016 | 2.136 | ok | 1 | 3.0% | 4756.2 | 25.4 | 2.17 | 752.9 | 89.2 / 10004 | 27.2 |
| jekyll | ruby | 10000 | 5 | 3 | 5.566 | 0.033 | 5.557 | 5.538 | 5.603 | ok | 1 | 0.6% | 1799.5 | 9.6 | 0.96 | 325.1 | 111.7 / 10001 | 52.8 |
| hugo | go | 10000 | 5 | 3 | 12.329 | 0.164 | 12.271 | 12.201 | 12.514 | ok | 1 | 1.3% | 814.9 | 4.3 | 3.67 | 4079.3 | 123.1 / 10003 | 34.3 |
| metalsmith-nunjucks | javascript | 10000 | 5 | 3 | 13.243 | 0.089 | 13.213 | 13.173 | 13.344 | ok | 2 | 0.7% | 756.8 | 4.0 | 1.38 | 644.0 | 88.9 / 10002 | 35.7 |
| metalsmith-handlebars | javascript | 10000 | 5 | 3 | 13.918 | 0.087 | 13.954 | 13.819 | 13.982 | ok | 1 | 0.6% | 716.6 | 3.8 | 1.36 | 663.8 | 88.9 / 10002 | 36.0 |
| astro | javascript | 10000 | 5 | 3 | 18.485 | 0.085 | 18.472 | 18.407 | 18.575 | ok | 1 | 0.5% | 541.3 | 2.9 | 1.36 | 1381.8 | 104.2 / 10001 | 44.6 |
| eleventy | javascript | 10000 | 5 | 3 | 20.070 | 0.060 | 20.102 | 20.000 | 20.106 | ok | 3 | 0.3% | 497.5 | 2.7 | 1.24 | 1310.5 | 83.0 / 10001 | 38.4 |
| hexo | javascript | 10000 | 5 | 3 | 25.273 | 0.211 | 25.203 | 25.105 | 25.510 | ok | 1 | 0.8% | 396.8 | 2.1 | 1.52 | 4370.3 | 125.4 / 10001 | 44.9 |
| publish | swift | 10000 | 5 | 3 | 33.224 | 0.194 | 33.331 | 33.000 | 33.340 | ok | 1 | 0.6% | 300.0 | 1.6 | 1.07 | 252.6 | 94.7 / 10004 | 158.6 |
| jigsaw | php | 10000 | 5 | 3 | 37.558 | 0.175 | 37.522 | 37.403 | 37.747 | ok | 1 | 0.5% | 266.5 | 1.4 | 1.00 | 404.4 | 93.0 / 10003 | 103.5 |
| nextjs-export | javascript | 10000 | 5 | 3 | 46.027 | 2.425 | 45.337 | 44.021 | 48.722 | ok | 2 | 5.3% | 220.6 | 1.2 | 2.48 | 1376.9 | 650.9 / 50021 | 55.4 |
| docfx | c# | 10000 | 5 | 3 | 52.014 | 1.202 | 51.457 | 51.191 | 53.393 | ok | =2 | 2.3% | 194.3 | 1.0 | 2.32 | 1110.7 | 102.8 / 10006 | 49.6 |
| starlight | javascript | 10000 | 5 | 3 | 52.991 | 0.235 | 52.898 | 52.817 | 53.258 | ok | =2 | 0.4% | 189.0 | 1.0 | 1.36 | 2440.8 | 386.7 / 10014 | 45.6 |
| pelican | python | 10000 | 5 | 3 | 80.368 | 0.564 | 80.397 | 79.790 | 80.917 | ok | 4 | 0.7% | 124.4 | 0.7 | 1.00 | 142.4 | 74.4 / 10001 | 42.0 |
| nanoc | ruby | 10000 | 5 | 3 | 80.396 | 1.219 | 80.831 | 79.020 | 81.338 | ok | 2 | 1.5% | 123.7 | 0.7 | 1.00 | 639.0 | 100.8 / 10001 | 36.1 |
| mkdocs | python | 10000 | 5 | 3 | 84.409 | 0.561 | 84.491 | 83.812 | 84.925 | ok | 3 | 0.7% | 118.4 | 0.6 | 1.00 | 296.7 | 90.4 / 10001 | 61.0 |
| middleman | ruby | 10000 | 5 | 3 | 92.894 | 1.248 | 92.470 | 91.913 | 94.298 | ok | 2 | 1.3% | 108.1 | 0.6 | 3.06 | 317.0 | 100.2 / 10002 | 110.3 |
| lektor | python | 10000 | 5 | 3 | 96.127 | 0.566 | 95.937 | 95.680 | 96.763 | ok | 5 | 0.6% | 104.2 | 0.5 | 0.99 | 164.7 | 83.1 / 10004 | 47.6 |
| hakyll | haskell | 10000 | 5 | 3 | 103.446 | 0.571 | 103.458 | 102.869 | 104.011 | ok | 3 | 0.6% | 96.7 | 0.5 | 3.38 | 821.8 | 107.5 / 10003 | 2411.2 |
| quartz | javascript | 10000 | 5 | 3 | 165.301 | 4.423 | 165.076 | 160.994 | 169.832 | ok | 2 | 2.7% | 60.6 | 0.3 | 3.52 | 6447.7 | 240.9 / 10012 | 201.8 |
| gatsby | javascript | 10000 | 5 | 3 | 178.052 | 9.643 | 178.009 | 168.431 | 187.717 | ok | 6 | 5.4% | 56.2 | 0.3 | 1.43 | 1656.7 | 197.0 / 20030 | 239.7 |
| nikola-mako | python | 10000 | 5 | 3 | 210.448 | 2.512 | 210.614 | 207.857 | 212.872 | ok | 7 | 1.2% | 47.5 | 0.3 | 0.98 | 441.2 | 86.3 / 10025 | 53.5 |
| zensical | python | 10000 | 5 | 3 | 219.533 | 1.553 | 219.179 | 218.188 | 221.233 | ok | 1 | 0.7% | 45.6 | 0.2 | 1.24 | 1586.5 | 204.0 / 10014 | 55.0 |
| mdbook | rust | 10000 | 5 | 3 | 250.868 | 3.703 | 249.634 | 247.939 | 255.030 | ok | 1 | 1.5% | 40.1 | 0.2 | 0.99 | 1628.8 | 124.7 / 10019 | 30.0 |
| analog | javascript | 10000 | 5 | 3 | 500.693 | 4.172 | 501.426 | 496.203 | 504.450 | ok | 3 | 0.8% | 19.9 | 0.1 | 1.12 | 6841.2 | 213.1 / 20008 | 64.4 |
| sveltekit | javascript | 10000 | 5 | 3 | 523.583 | 8.085 | 519.753 | 518.126 | 532.872 | ok | 8 | 1.5% | 19.2 | 0.1 | 1.38 | 6598.4 | 198.3 / 20020 | 40.2 |
| sphinx | python | 10000 | 5 | 3 | 718.961 | 14.376 | 718.406 | 704.870 | 733.607 | ok | 4 | 2.0% | 13.9 | 0.1 | 1.00 | 6893.9 | 134.4 / 10005 | 55.8 |
| nuxt-content | javascript | 10000 | 5 | 3 | 772.449 | 4.303 | 772.247 | 768.250 | 776.848 | ok | 4 | 0.6% | 12.9 | 0.1 | 1.11 | 6387.2 | 463.9 / 20053 | 55.7 |
| docusaurus | javascript | 10000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 106.6 |
| dumi | javascript | 10000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 83.2 |
| nextra | javascript | 10000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 82.8 |
| observable-framework | javascript | 10000 | 5 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 46.8 |
| quarto | typescript | 10000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 48.5 |
| vitepress | javascript | 10000 | 5 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 36.3 |
| vuepress | javascript | 10000 | 5 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 39.4 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### G v1 · nf 10000, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 2.103 | 3.0% | 2.016–2.136 |
| 2 | quartz | 165.076 | 2.7% | 160.994–169.832 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint 90616b2b906d

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 5.557 | 0.6% | 5.538–5.603 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 12.271 | 1.3% | 12.201–12.514 |
| 2 | metalsmith-nunjucks | 13.213 | 0.7% | 13.173–13.344 |
| 3 | eleventy | 20.102 | 0.3% | 20.000–20.106 |
| 4 | pelican | 80.397 | 0.7% | 79.790–80.917 |
| 5 | lektor | 95.937 | 0.6% | 95.680–96.763 |
| 6 | gatsby | 178.009 | 5.4% | 168.431–187.717 |
| 7 | nikola-mako | 210.614 | 1.2% | 207.857–212.872 |
| 8 | sveltekit | 519.753 | 1.5% | 518.126–532.872 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 13.954 | 0.6% | 13.819–13.982 |
| 2 | middleman | 92.470 | 1.3% | 91.913–94.298 |
| 3 | analog | 501.426 | 0.8% | 496.203–504.450 |
| 4 | nuxt-content | 772.247 | 0.6% | 768.250–776.848 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint fe502e5b5baa

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | astro | 18.472 | 0.5% | 18.407–18.575 |
| =2 | docfx | 51.457 | 2.3% | 51.191–53.393 |
| =2 | starlight | 52.898 | 0.4% | 52.817–53.258 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hexo | 25.203 | 0.8% | 25.105–25.510 |
| 2 | nextjs-export | 45.337 | 5.3% | 44.021–48.722 |
| 3 | mkdocs | 84.491 | 0.7% | 83.812–84.925 |
| 4 | sphinx | 718.406 | 2.0% | 704.870–733.607 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint ba134637a49c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | publish | 33.331 | 0.6% | 33.000–33.340 |
| 2 | nanoc | 80.831 | 1.5% | 79.020–81.338 |
| 3 | hakyll | 103.458 | 0.6% | 102.869–104.011 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 37.522 | 0.5% | 37.403–37.747 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zensical | 219.179 | 0.7% | 218.188–221.233 |

### G v1 · nf 10000, cs 5 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mdbook | 249.634 | 1.5% | 247.939–255.030 |

## Caveats

- T9: oom means the generator exceeded the container memory limit, which is the same for every generator; it is an outcome, not a time.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

- docusaurus (failed): SSGBERK_VERIFY_FAIL build exited 134
- dumi (failed): SSGBERK_VERIFY_FAIL build exited 134
- nextra (oom): oom
- observable-framework (timeout): timeout
- quarto (oom): oom
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
- vuepress (oom): oom
