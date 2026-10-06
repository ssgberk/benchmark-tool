# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 11:05:49 UTC
- Completed: 2026-10-06 11:45:15 UTC
- Commit: 54be4010a4aabbba9c5580d321dcc52e23460537

Suite: P v1 · cell 2/2 (nf 50, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 50 | 50 | 5 | 0.158 | 0.003 | 0.157 | 0.156 | 0.163 | ok | 1 | 1.7% | 319.3 | 16.4 | 3.04 | 68.1 | 4.4 / 54 | 27.0 |
| mdbook | rust | 50 | 50 | 5 | 0.230 | 0.006 | 0.228 | 0.224 | 0.241 | ok | 2 | 2.8% | 218.8 | 11.2 | 1.00 | 83.8 | 6.2 / 69 | 22.5 |
| hugo | go | 50 | 50 | 10 | 0.551 | 0.006 | 0.551 | 0.537 | 0.559 | ok | 3 | 1.1% | 90.7 | 4.7 | 3.65 | 269.2 | 5.7 / 53 | 26.7 |
| metalsmith-nunjucks | javascript | 50 | 50 | 5 | 0.742 | 0.020 | 0.733 | 0.725 | 0.775 | ok | =4 | 2.7% | 68.2 | 3.5 | 1.47 | 148.9 | 4.3 / 52 | 37.5 |
| eleventy | javascript | 50 | 50 | 5 | 0.772 | 0.013 | 0.772 | 0.755 | 0.787 | ok | 1 | 1.7% | 64.8 | 3.3 | 1.57 | 298.2 | 4.1 / 51 | 39.7 |
| metalsmith-handlebars | javascript | 50 | 50 | 5 | 0.774 | 0.010 | 0.773 | 0.763 | 0.791 | ok | =4 | 1.3% | 64.7 | 3.3 | 1.49 | 124.1 | 4.3 / 52 | 37.6 |
| publish | swift | 50 | 50 | 5 | 0.998 | 0.004 | 0.998 | 0.992 | 1.004 | ok | 6 | 0.4% | 50.1 | 2.6 | 1.02 | 36.0 | 3.9 / 54 | 124.5 |
| jigsaw | php | 50 | 50 | 5 | 1.336 | 0.003 | 1.336 | 1.333 | 1.341 | ok | 1 | 0.2% | 37.4 | 1.9 | 1.00 | 47.5 | 4.2 / 53 | 111.7 |
| hexo | javascript | 50 | 50 | 5 | 2.103 | 0.074 | 2.075 | 2.050 | 2.232 | ok | 7 | 3.5% | 24.1 | 1.2 | 1.34 | 437.6 | 6.2 / 51 | 49.3 |
| astro | javascript | 50 | 50 | 5 | 2.510 | 0.018 | 2.512 | 2.482 | 2.529 | ok | 8 | 0.7% | 19.9 | 1.0 | 1.49 | 882.8 | 5.1 / 51 | 49.2 |
| nanoc | ruby | 50 | 50 | 5 | 2.616 | 0.066 | 2.638 | 2.521 | 2.673 | ok | 1 | 2.5% | 19.0 | 1.0 | 1.00 | 109.0 | 4.9 / 51 | 44.2 |
| pelican | python | 50 | 50 | 5 | 2.642 | 0.034 | 2.628 | 2.622 | 2.702 | ok | 1 | 1.3% | 19.0 | 1.0 | 1.00 | 46.4 | 3.6 / 51 | 49.0 |
| lektor | python | 50 | 50 | 5 | 3.157 | 0.041 | 3.144 | 3.122 | 3.224 | ok | 9 | 1.3% | 15.9 | 0.8 | 1.00 | 57.2 | 4.1 / 54 | 44.6 |
| jekyll | ruby | 50 | 50 | 5 | 3.917 | 0.020 | 3.921 | 3.887 | 3.941 | ok | =10 | 0.5% | 12.8 | 0.7 | 1.00 | 110.5 | 5.5 / 51 | 52.3 |
| middleman | ruby | 50 | 50 | 5 | 3.961 | 0.033 | 3.978 | 3.911 | 3.986 | ok | =10 | 0.8% | 12.6 | 0.6 | 2.97 | 100.4 | 4.9 / 52 | 99.1 |
| vuepress | javascript | 50 | 50 | 5 | 4.484 | 0.083 | 4.503 | 4.383 | 4.586 | ok | 1 | 1.9% | 11.1 | 0.6 | 1.73 | 1236.8 | 10.8 / 109 | 41.4 |
| starlight | javascript | 50 | 50 | 5 | 4.951 | 0.041 | 4.970 | 4.888 | 4.986 | ok | 1 | 0.8% | 10.1 | 0.5 | 1.50 | 1406.1 | 15.2 / 64 | 48.0 |
| mkdocs | python | 50 | 50 | 5 | 5.139 | 0.066 | 5.116 | 5.073 | 5.230 | ok | 1 | 1.3% | 9.8 | 0.5 | 1.00 | 55.5 | 4.4 / 51 | 39.3 |
| hakyll | haskell | 50 | 50 | 5 | 5.761 | 0.507 | 5.545 | 5.507 | 6.668 | ok | 12 | 8.8% | 9.0 | 0.5 | 3.17 | 945.6 | 4.8 / 53 | 2328.1 |
| nextjs-export | javascript | 50 | 50 | 5 | 5.762 | 0.229 | 5.797 | 5.479 | 6.037 | ok | 2 | 4.0% | 8.6 | 0.4 | 2.99 | 1383.8 | 25.2 / 271 | 55.2 |
| analog | javascript | 50 | 50 | 5 | 6.672 | 0.062 | 6.659 | 6.595 | 6.759 | ok | 2 | 0.9% | 7.5 | 0.4 | 1.80 | 1841.7 | 10.2 / 108 | 59.4 |
| docfx | c# | 50 | 50 | 5 | 6.740 | 0.457 | 6.822 | 5.960 | 7.113 | ok | 1 | 6.8% | 7.3 | 0.4 | 2.24 | 499.7 | 4.4 / 56 | 66.5 |
| vitepress | javascript | 50 | 50 | 5 | 7.545 | 0.114 | 7.537 | 7.372 | 7.685 | ok | 13 | 1.5% | 6.6 | 0.3 | 1.45 | 1121.2 | 14.2 / 162 | 38.6 |
| nikola-mako | python | 50 | 50 | 5 | 8.861 | 0.082 | 8.838 | 8.758 | 8.959 | ok | 2 | 0.9% | 5.7 | 0.3 | 0.55 | 66.6 | 4.4 / 75 | 49.6 |
| zensical | python | 50 | 50 | 5 | 13.886 | 0.077 | 13.852 | 13.815 | 14.012 | ok | 1 | 0.6% | 3.6 | 0.2 | 1.01 | 140.1 | 10.5 / 64 | 47.8 |
| quartz | javascript | 50 | 50 | 5 | 15.021 | 0.156 | 14.987 | 14.860 | 15.252 | ok | 14 | 1.0% | 3.3 | 0.2 | 1.36 | 802.1 | 10.7 / 62 | 267.1 |
| nuxt-content | javascript | 50 | 50 | 5 | 20.745 | 0.195 | 20.704 | 20.564 | 21.065 | ok | 3 | 0.9% | 2.4 | 0.1 | 1.50 | 1599.7 | 21.5 / 153 | 58.8 |
| observable-framework | javascript | 50 | 50 | 5 | 24.769 | 0.190 | 24.817 | 24.468 | 24.985 | ok | 15 | 0.8% | 2.0 | 0.1 | 1.24 | 772.4 | 5.6 / 57 | 41.7 |
| sveltekit | javascript | 50 | 50 | 5 | 27.054 | 0.140 | 27.002 | 26.913 | 27.219 | ok | 1 | 0.5% | 1.9 | 0.1 | 1.50 | 958.0 | 8.7 / 120 | 36.6 |
| gatsby | javascript | 50 | 50 | 5 | 28.868 | 0.992 | 28.410 | 27.905 | 30.363 | ok | 4 | 3.4% | 1.8 | 0.1 | 1.63 | 909.0 | 9.6 / 130 | 235.6 |
| sphinx | python | 50 | 50 | 5 | 31.355 | 0.520 | 31.325 | 30.917 | 32.204 | ok | 1 | 1.7% | 1.6 | 0.1 | 1.00 | 437.3 | 6.6 / 55 | 46.4 |
| nextra | javascript | 50 | 50 | 5 | 54.793 | 0.701 | 54.492 | 54.241 | 55.946 | ok | 2 | 1.3% | 0.9 | 0.0 | 1.18 | 3133.5 | 65.9 / 276 | 78.7 |
| quarto | typescript | 50 | 50 | 5 | 98.618 | 0.297 | 98.602 | 98.269 | 98.994 | ok | 1 | 0.3% | 0.5 | 0.0 | 1.03 | 985.0 | 6.1 / 63 | 41.6 |
| docusaurus | javascript | 50 | 50 | 5 | 129.751 | 0.924 | 129.904 | 128.213 | 130.692 | ok | 16 | 0.7% | 0.4 | 0.0 | 1.84 | 4235.9 | 31.1 / 171 | 106.2 |
| dumi | javascript | 50 | 50 | 5 | 151.596 | 1.065 | 151.519 | 149.991 | 152.647 | ok | 17 | 0.7% | 0.3 | 0.0 | 1.25 | 3486.7 | 25.4 / 168 | 86.6 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### P v1 · nf 50, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 0.157 | 1.7% | 0.156–0.163 |
| 2 | mdbook | 0.228 | 2.8% | 0.224–0.241 |
| 3 | hugo | 0.551 | 1.1% | 0.537–0.559 |
| =4 | metalsmith-nunjucks | 0.733 | 2.7% | 0.725–0.775 |
| =4 | metalsmith-handlebars | 0.773 | 1.3% | 0.763–0.791 |
| 6 | publish | 0.998 | 0.4% | 0.992–1.004 |
| 7 | hexo | 2.075 | 3.5% | 2.050–2.232 |
| 8 | astro | 2.512 | 0.7% | 2.482–2.529 |
| 9 | lektor | 3.144 | 1.3% | 3.122–3.224 |
| =10 | jekyll | 3.921 | 0.5% | 3.887–3.941 |
| =10 | middleman | 3.978 | 0.8% | 3.911–3.986 |
| 12 | hakyll | 5.545 | 8.8% | 5.507–6.668 |
| 13 | vitepress | 7.537 | 1.5% | 7.372–7.685 |
| 14 | quartz | 14.987 | 1.0% | 14.860–15.252 |
| 15 | observable-framework | 24.817 | 0.8% | 24.468–24.985 |
| 16 | docusaurus | 129.904 | 0.7% | 128.213–130.692 |
| 17 | dumi | 151.519 | 0.7% | 149.991–152.647 |

### P v1 · nf 50, cs 50 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | eleventy | 0.772 | 1.7% | 0.755–0.787 |
| 2 | nikola-mako | 8.838 | 0.9% | 8.758–8.959 |

### P v1 · nf 50, cs 50 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 1.336 | 0.2% | 1.333–1.341 |

### P v1 · nf 50, cs 50 · profile core · fingerprint f7f947e641fa

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nanoc | 2.638 | 2.5% | 2.521–2.673 |
| 2 | analog | 6.659 | 0.9% | 6.595–6.759 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 2.628 | 1.3% | 2.622–2.702 |
| 2 | nextjs-export | 5.797 | 4.0% | 5.479–6.037 |
| 3 | nuxt-content | 20.704 | 0.9% | 20.564–21.065 |
| 4 | gatsby | 28.410 | 3.4% | 27.905–30.363 |

### P v1 · nf 50, cs 50 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | vuepress | 4.503 | 1.9% | 4.383–4.586 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | starlight | 4.970 | 0.8% | 4.888–4.986 |

### P v1 · nf 50, cs 50 · profile core · fingerprint fe502e5b5baa

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mkdocs | 5.116 | 1.3% | 5.073–5.230 |
| 2 | nextra | 54.492 | 1.3% | 54.241–55.946 |

### P v1 · nf 50, cs 50 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | docfx | 6.822 | 6.8% | 5.960–7.113 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 6fc37d2dc496

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zensical | 13.852 | 0.6% | 13.815–14.012 |

### P v1 · nf 50, cs 50 · profile core · fingerprint dbc7b3c4cf92

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | sveltekit | 27.002 | 0.5% | 26.913–27.219 |

### P v1 · nf 50, cs 50 · profile core · fingerprint c5ccc7094d75

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | sphinx | 31.325 | 1.7% | 30.917–32.204 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | quarto | 98.602 | 0.3% | 98.269–98.994 |

## Caveats

- T5: at 100 files or fewer, bundler-dominated JavaScript generators (Gatsby, Next.js, Astro, VitePress) mostly measure bundler start-up, not content handling. Read the full matrix and the scaling exponent; never quote one small cell as the result.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

None.
