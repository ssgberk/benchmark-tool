# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 11:15:49 UTC
- Completed: 2026-10-06 12:33:25 UTC
- Commit: 54be4010a4aabbba9c5580d321dcc52e23460537

Suite: M v1 · cell 1/2 (nf 1000, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 1000 | 5 | 5 | 0.289 | 0.006 | 0.287 | 0.285 | 0.299 | ok | 1 | 2.0% | 3489.1 | 18.7 | 2.56 | 102.8 | 8.9 / 1004 | 23.7 |
| metalsmith-handlebars | javascript | 1000 | 5 | 5 | 1.000 | 0.017 | 1.009 | 0.981 | 1.014 | ok | 1 | 1.7% | 990.9 | 5.3 | 1.56 | 207.3 | 8.9 / 1002 | 35.0 |
| metalsmith-nunjucks | javascript | 1000 | 5 | 5 | 1.139 | 0.016 | 1.140 | 1.114 | 1.157 | ok | 1 | 1.4% | 877.1 | 4.7 | 1.56 | 204.4 | 8.9 / 1002 | 37.2 |
| hugo | go | 1000 | 5 | 5 | 1.162 | 0.018 | 1.162 | 1.139 | 1.181 | ok | 1 | 1.6% | 860.4 | 4.6 | 3.61 | 487.2 | 12.3 / 1003 | 24.1 |
| jekyll | ruby | 1000 | 5 | 5 | 1.264 | 0.012 | 1.267 | 1.252 | 1.279 | ok | 1 | 0.9% | 789.1 | 4.2 | 1.00 | 106.0 | 11.2 / 1001 | 53.3 |
| eleventy | javascript | 1000 | 5 | 5 | 2.202 | 0.080 | 2.167 | 2.125 | 2.315 | ok | 1 | 3.6% | 461.5 | 2.5 | 1.44 | 336.1 | 8.3 / 1001 | 32.9 |
| hexo | javascript | 1000 | 5 | 5 | 2.506 | 0.066 | 2.511 | 2.407 | 2.593 | ok | 2 | 2.6% | 398.2 | 2.1 | 1.57 | 723.1 | 12.5 / 1001 | 40.0 |
| publish | swift | 1000 | 5 | 5 | 2.544 | 0.010 | 2.540 | 2.534 | 2.560 | ok | 2 | 0.4% | 393.7 | 2.1 | 1.12 | 54.3 | 9.5 / 1004 | 122.0 |
| jigsaw | php | 1000 | 5 | 5 | 2.658 | 0.009 | 2.658 | 2.648 | 2.671 | ok | 2 | 0.3% | 376.2 | 2.0 | 1.00 | 75.1 | 9.3 / 1003 | 73.6 |
| astro | javascript | 1000 | 5 | 5 | 3.641 | 0.093 | 3.613 | 3.542 | 3.792 | ok | 1 | 2.6% | 276.8 | 1.5 | 1.47 | 819.3 | 10.4 / 1001 | 46.9 |
| mdbook | rust | 1000 | 5 | 5 | 3.708 | 0.017 | 3.709 | 3.687 | 3.727 | ok | 3 | 0.5% | 269.6 | 1.4 | 0.99 | 170.3 | 12.7 / 1019 | 30.2 |
| pelican | python | 1000 | 5 | 5 | 6.756 | 0.034 | 6.775 | 6.713 | 6.788 | ok | 1 | 0.5% | 147.6 | 0.8 | 1.00 | 51.5 | 7.4 / 1001 | 48.0 |
| starlight | javascript | 1000 | 5 | 5 | 8.038 | 0.047 | 8.054 | 7.973 | 8.097 | ok | 4 | 0.6% | 124.2 | 0.7 | 1.45 | 1105.3 | 38.9 / 1014 | 51.5 |
| docfx | c# | 1000 | 5 | 5 | 8.696 | 0.104 | 8.671 | 8.554 | 8.817 | ok | =3 | 1.2% | 115.3 | 0.6 | 2.63 | 220.2 | 10.3 / 1006 | 50.0 |
| lektor | python | 1000 | 5 | 5 | 8.878 | 0.041 | 8.887 | 8.825 | 8.933 | ok | 5 | 0.5% | 112.5 | 0.6 | 0.99 | 72.7 | 8.3 / 1004 | 49.4 |
| mkdocs | python | 1000 | 5 | 5 | 9.319 | 0.114 | 9.370 | 9.152 | 9.434 | ok | 1 | 1.2% | 106.7 | 0.5 | 1.00 | 59.3 | 9.0 / 1001 | 44.7 |
| nextjs-export | javascript | 1000 | 5 | 5 | 9.321 | 0.596 | 9.290 | 8.708 | 10.066 | ok | =3 | 6.4% | 107.6 | 0.6 | 2.98 | 1423.9 | 65.6 / 5021 | 57.7 |
| middleman | ruby | 1000 | 5 | 5 | 9.480 | 0.089 | 9.482 | 9.391 | 9.616 | ok | 1 | 0.9% | 105.5 | 0.6 | 2.87 | 123.7 | 10.0 / 1002 | 100.1 |
| vuepress | javascript | 1000 | 5 | 5 | 9.621 | 0.138 | 9.573 | 9.502 | 9.809 | ok | =3 | 1.4% | 104.5 | 0.6 | 1.69 | 2131.4 | 23.0 / 2009 | 40.2 |
| nanoc | ruby | 1000 | 5 | 5 | 9.723 | 0.085 | 9.725 | 9.621 | 9.853 | ok | 2 | 0.9% | 102.8 | 0.6 | 1.00 | 156.9 | 10.1 / 1001 | 38.8 |
| hakyll | haskell | 1000 | 5 | 5 | 11.548 | 0.090 | 11.530 | 11.419 | 11.657 | ok | 6 | 0.8% | 86.7 | 0.5 | 3.32 | 549.1 | 10.8 / 1003 | 2434.8 |
| vitepress | javascript | 1000 | 5 | 5 | 16.337 | 0.079 | 16.338 | 16.257 | 16.426 | ok | 1 | 0.5% | 61.2 | 0.3 | 1.47 | 1825.7 | 73.2 / 3012 | 40.9 |
| analog | javascript | 1000 | 5 | 5 | 19.057 | 0.320 | 18.960 | 18.782 | 19.608 | ok | 6 | 1.7% | 52.7 | 0.3 | 1.43 | 2723.8 | 21.8 / 2008 | 61.1 |
| quartz | javascript | 1000 | 5 | 5 | 23.651 | 0.075 | 23.649 | 23.559 | 23.749 | ok | 7 | 0.3% | 42.3 | 0.2 | 3.17 | 2267.0 | 24.2 / 1012 | 274.7 |
| nikola-mako | python | 1000 | 5 | 5 | 24.691 | 0.291 | 24.574 | 24.412 | 25.139 | ok | 8 | 1.2% | 40.7 | 0.2 | 0.84 | 101.0 | 8.8 / 1025 | 49.7 |
| zensical | python | 1000 | 5 | 5 | 33.008 | 0.338 | 32.850 | 32.723 | 33.493 | ok | 9 | 1.0% | 30.4 | 0.2 | 1.04 | 219.8 | 20.8 / 1014 | 56.2 |
| sveltekit | javascript | 1000 | 5 | 5 | 35.229 | 0.336 | 35.117 | 34.788 | 35.618 | ok | 1 | 1.0% | 28.5 | 0.2 | 1.48 | 1399.1 | 19.9 / 2020 | 41.7 |
| gatsby | javascript | 1000 | 5 | 5 | 35.803 | 0.238 | 35.855 | 35.405 | 35.993 | ok | 10 | 0.7% | 27.9 | 0.1 | 1.59 | 789.0 | 20.7 / 2030 | 236.4 |
| nuxt-content | javascript | 1000 | 5 | 5 | 41.329 | 0.832 | 40.927 | 40.826 | 42.796 | ok | 11 | 2.0% | 24.4 | 0.1 | 1.29 | 1809.0 | 47.1 / 2053 | 57.1 |
| sphinx | python | 1000 | 5 | 5 | 54.318 | 0.384 | 54.480 | 53.771 | 54.719 | ok | 2 | 0.7% | 18.4 | 0.1 | 1.00 | 760.6 | 13.4 / 1005 | 46.7 |
| nextra | javascript | 1000 | 5 | 5 | 90.720 | 0.582 | 90.572 | 90.166 | 91.346 | ok | 7 | 0.6% | 11.0 | 0.1 | 1.33 | 6227.8 | 145.5 / 5026 | 69.7 |
| observable-framework | javascript | 1000 | 5 | 5 | 116.649 | 0.708 | 116.514 | 115.868 | 117.792 | ok | 12 | 0.6% | 8.6 | 0.0 | 1.15 | 645.8 | 12.3 / 1007 | 46.8 |
| docusaurus | javascript | 1000 | 5 | 5 | 257.523 | 4.145 | 255.213 | 253.323 | 262.630 | ok | 13 | 1.6% | 3.9 | 0.0 | 1.79 | 6387.7 | 70.2 / 3021 | 101.4 |
| quarto | typescript | 1000 | 5 | 5 | 562.874 | 16.961 | 560.841 | 541.194 | 588.266 | ok | 3 | 3.0% | 1.8 | 0.0 | 1.01 | 939.8 | 26.2 / 1013 | 36.0 |
| dumi | javascript | 1000 | 5 | 5 | 675.030 | 9.449 | 677.493 | 664.908 | 687.077 | ok | 1 | 1.4% | 1.5 | 0.0 | 1.16 | 4835.9 | 62.0 / 2018 | 84.7 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### M v1 · nf 1000, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 0.287 | 2.0% | 0.285–0.299 |
| 2 | publish | 2.540 | 0.4% | 2.534–2.560 |
| 3 | mdbook | 3.709 | 0.5% | 3.687–3.727 |
| 4 | starlight | 8.054 | 0.6% | 7.973–8.097 |
| 5 | lektor | 8.887 | 0.5% | 8.825–8.933 |
| 6 | hakyll | 11.530 | 0.8% | 11.419–11.657 |
| 7 | quartz | 23.649 | 0.3% | 23.559–23.749 |
| 8 | nikola-mako | 24.574 | 1.2% | 24.412–25.139 |
| 9 | zensical | 32.850 | 1.0% | 32.723–33.493 |
| 10 | gatsby | 35.855 | 0.7% | 35.405–35.993 |
| 11 | nuxt-content | 40.927 | 2.0% | 40.826–42.796 |
| 12 | observable-framework | 116.514 | 0.6% | 115.868–117.792 |
| 13 | docusaurus | 255.213 | 1.6% | 253.323–262.630 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 1.009 | 1.7% | 0.981–1.014 |
| 2 | hexo | 2.511 | 2.6% | 2.407–2.593 |
| 3 | quarto | 560.841 | 3.0% | 541.194–588.266 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 0719afa5a160

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-nunjucks | 1.140 | 1.4% | 1.114–1.157 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 1.162 | 1.6% | 1.139–1.181 |
| 2 | jigsaw | 2.658 | 0.3% | 2.648–2.671 |
| =3 | docfx | 8.671 | 1.2% | 8.554–8.817 |
| =3 | nextjs-export | 9.290 | 6.4% | 8.708–10.066 |
| =3 | vuepress | 9.573 | 1.4% | 9.502–9.809 |
| 6 | analog | 18.960 | 1.7% | 18.782–19.608 |
| 7 | nextra | 90.572 | 0.6% | 90.166–91.346 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 1.267 | 0.9% | 1.252–1.279 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | eleventy | 2.167 | 3.6% | 2.125–2.315 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 6fc37d2dc496

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | astro | 3.613 | 2.6% | 3.542–3.792 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint ba134637a49c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 6.775 | 0.5% | 6.713–6.788 |
| 2 | sphinx | 54.480 | 0.7% | 53.771–54.719 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 2f62636d600c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mkdocs | 9.370 | 1.2% | 9.152–9.434 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | middleman | 9.482 | 0.9% | 9.391–9.616 |
| 2 | nanoc | 9.725 | 0.9% | 9.621–9.853 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | vitepress | 16.338 | 0.5% | 16.257–16.426 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | sveltekit | 35.117 | 1.0% | 34.788–35.618 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 4f6fd13ef728

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | dumi | 677.493 | 1.4% | 664.908–687.077 |

## Failed / timeout / oom / nonconformant / unsupported

None.
