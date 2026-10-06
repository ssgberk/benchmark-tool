# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 11:05:48 UTC
- Completed: 2026-10-06 11:49:55 UTC
- Commit: 54be4010a4aabbba9c5580d321dcc52e23460537

Suite: P v1 · cell 1/2 (nf 50, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 50 | 5 | 5 | 0.032 | 0.000 | 0.032 | 0.032 | 0.032 | ok | 1 | 1.0% | 1551.3 | 8.3 | 1.53 | 33.7 | 0.5 / 54 | 26.8 |
| mdbook | rust | 50 | 5 | 5 | 0.058 | 0.001 | 0.058 | 0.058 | 0.060 | ok | 1 | 1.5% | 861.6 | 4.4 | 0.99 | 16.8 | 0.9 / 69 | 21.9 |
| hugo | go | 50 | 5 | 5 | 0.113 | 0.002 | 0.113 | 0.110 | 0.116 | ok | 2 | 2.1% | 442.6 | 2.4 | 2.76 | 87.4 | 0.6 / 53 | 48.1 |
| publish | swift | 50 | 5 | 5 | 0.139 | 0.003 | 0.139 | 0.136 | 0.144 | ok | 3 | 2.2% | 358.5 | 1.9 | 1.13 | 30.6 | 0.5 / 54 | 124.5 |
| jigsaw | php | 50 | 5 | 5 | 0.252 | 0.004 | 0.250 | 0.249 | 0.260 | ok | 4 | 1.7% | 200.1 | 1.1 | 1.00 | 41.2 | 0.5 / 53 | 61.1 |
| metalsmith-nunjucks | javascript | 50 | 5 | 5 | 0.253 | 0.008 | 0.249 | 0.243 | 0.265 | ok | 1 | 3.3% | 200.8 | 1.1 | 1.51 | 85.8 | 0.4 / 52 | 35.4 |
| metalsmith-handlebars | javascript | 50 | 5 | 5 | 0.271 | 0.007 | 0.269 | 0.263 | 0.280 | ok | 2 | 2.6% | 185.6 | 1.0 | 1.59 | 91.0 | 0.4 / 52 | 35.5 |
| mkdocs | python | 50 | 5 | 5 | 0.406 | 0.009 | 0.406 | 0.395 | 0.416 | ok | 1 | 2.1% | 123.2 | 0.6 | 1.00 | 33.2 | 0.5 / 51 | 42.7 |
| pelican | python | 50 | 5 | 5 | 0.636 | 0.002 | 0.636 | 0.634 | 0.639 | ok | 5 | 0.3% | 78.6 | 0.4 | 1.00 | 42.1 | 0.4 / 51 | 43.4 |
| jekyll | ruby | 50 | 5 | 5 | 0.747 | 0.027 | 0.749 | 0.720 | 0.791 | ok | 1 | 3.7% | 66.8 | 0.4 | 1.00 | 80.9 | 0.6 / 51 | 43.7 |
| lektor | python | 50 | 5 | 5 | 0.762 | 0.016 | 0.768 | 0.742 | 0.779 | ok | 6 | 2.1% | 65.1 | 0.3 | 0.99 | 48.1 | 0.4 / 54 | 43.9 |
| eleventy | javascript | 50 | 5 | 5 | 0.797 | 0.003 | 0.798 | 0.792 | 0.800 | ok | 7 | 0.4% | 62.6 | 0.3 | 1.38 | 133.8 | 0.4 / 51 | 35.8 |
| docfx | c# | 50 | 5 | 5 | 0.984 | 0.006 | 0.985 | 0.977 | 0.993 | ok | 2 | 0.7% | 50.8 | 0.3 | 1.54 | 132.8 | 0.5 / 56 | 52.6 |
| hakyll | haskell | 50 | 5 | 5 | 1.059 | 0.017 | 1.066 | 1.030 | 1.076 | ok | 3 | 1.7% | 46.9 | 0.3 | 2.44 | 318.0 | 0.5 / 53 | 2405.1 |
| hexo | javascript | 50 | 5 | 5 | 1.061 | 0.008 | 1.062 | 1.048 | 1.070 | ok | 2 | 0.8% | 47.1 | 0.3 | 1.39 | 149.2 | 0.6 / 51 | 40.9 |
| nanoc | ruby | 50 | 5 | 5 | 1.221 | 0.019 | 1.213 | 1.207 | 1.254 | ok | 8 | 1.6% | 41.2 | 0.2 | 1.00 | 75.3 | 0.5 / 51 | 43.4 |
| astro | javascript | 50 | 5 | 5 | 1.561 | 0.070 | 1.535 | 1.486 | 1.669 | ok | =4 | 4.5% | 32.6 | 0.2 | 1.44 | 613.1 | 0.5 / 51 | 53.1 |
| vuepress | javascript | 50 | 5 | 5 | 1.688 | 0.120 | 1.612 | 1.582 | 1.835 | ok | =4 | 7.1% | 31.0 | 0.2 | 1.63 | 503.3 | 1.2 / 109 | 37.9 |
| zensical | python | 50 | 5 | 5 | 1.798 | 0.007 | 1.799 | 1.791 | 1.805 | ok | 1 | 0.4% | 27.8 | 0.1 | 1.01 | 70.0 | 1.5 / 64 | 52.6 |
| middleman | ruby | 50 | 5 | 5 | 1.882 | 0.018 | 1.875 | 1.863 | 1.904 | ok | 6 | 0.9% | 26.7 | 0.1 | 1.69 | 97.1 | 0.5 / 52 | 113.3 |
| vitepress | javascript | 50 | 5 | 5 | 1.993 | 0.106 | 1.947 | 1.911 | 2.176 | ok | 1 | 5.3% | 25.7 | 0.1 | 1.64 | 453.1 | 1.8 / 162 | 40.0 |
| quartz | javascript | 50 | 5 | 5 | 2.679 | 0.015 | 2.677 | 2.659 | 2.701 | ok | 1 | 0.6% | 18.7 | 0.1 | 1.58 | 453.3 | 1.3 / 62 | 251.1 |
| starlight | javascript | 50 | 5 | 5 | 2.900 | 0.137 | 2.839 | 2.814 | 3.142 | ok | 7 | 4.7% | 17.6 | 0.1 | 1.51 | 835.0 | 2.1 / 64 | 48.4 |
| sphinx | python | 50 | 5 | 5 | 3.627 | 0.025 | 3.619 | 3.599 | 3.663 | ok | 9 | 0.7% | 13.8 | 0.1 | 1.00 | 100.4 | 0.7 / 55 | 44.9 |
| nikola-mako | python | 50 | 5 | 5 | 4.807 | 0.013 | 4.814 | 4.789 | 4.819 | ok | 3 | 0.3% | 10.4 | 0.1 | 0.17 | 64.0 | 0.7 / 75 | 50.1 |
| sveltekit | javascript | 50 | 5 | 5 | 5.446 | 0.100 | 5.419 | 5.341 | 5.587 | ok | 10 | 1.8% | 9.2 | 0.0 | 1.62 | 731.7 | 1.1 / 120 | 40.2 |
| observable-framework | javascript | 50 | 5 | 5 | 5.788 | 0.095 | 5.773 | 5.667 | 5.902 | ok | 11 | 1.6% | 8.7 | 0.0 | 1.37 | 607.2 | 0.7 / 57 | 47.0 |
| nextjs-export | javascript | 50 | 5 | 5 | 6.259 | 0.041 | 6.254 | 6.220 | 6.326 | ok | 12 | 0.6% | 8.0 | 0.0 | 3.13 | 1383.1 | 3.9 / 271 | 47.0 |
| analog | javascript | 50 | 5 | 5 | 7.049 | 0.059 | 7.044 | 6.961 | 7.112 | ok | 13 | 0.8% | 7.1 | 0.0 | 1.96 | 1652.0 | 1.7 / 108 | 59.9 |
| nuxt-content | javascript | 50 | 5 | 5 | 7.659 | 0.053 | 7.627 | 7.617 | 7.740 | ok | 14 | 0.7% | 6.6 | 0.0 | 1.60 | 1124.2 | 3.9 / 153 | 56.3 |
| docusaurus | javascript | 50 | 5 | 5 | 14.243 | 0.150 | 14.325 | 14.045 | 14.379 | ok | 4 | 1.1% | 3.5 | 0.0 | 2.15 | 1798.9 | 4.1 / 171 | 76.7 |
| gatsby | javascript | 50 | 5 | 5 | 15.054 | 0.179 | 15.007 | 14.822 | 15.266 | ok | 8 | 1.2% | 3.3 | 0.0 | 1.71 | 708.5 | 2.1 / 130 | 209.8 |
| nextra | javascript | 50 | 5 | 5 | 25.108 | 0.304 | 25.085 | 24.812 | 25.506 | ok | 15 | 1.2% | 2.0 | 0.0 | 1.39 | 1777.0 | 7.9 / 276 | 89.8 |
| dumi | javascript | 50 | 5 | 5 | 25.980 | 0.196 | 25.935 | 25.752 | 26.292 | ok | 16 | 0.8% | 1.9 | 0.0 | 1.45 | 1585.3 | 4.1 / 118 | 90.3 |
| quarto | typescript | 50 | 5 | 5 | 40.141 | 0.250 | 40.230 | 39.843 | 40.374 | ok | 1 | 0.6% | 1.2 | 0.0 | 1.03 | 409.9 | 1.4 / 63 | 44.8 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### P v1 · nf 50, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 0.032 | 1.0% | 0.032–0.032 |
| 2 | metalsmith-handlebars | 0.269 | 2.6% | 0.263–0.280 |
| 3 | hakyll | 1.066 | 1.7% | 1.030–1.076 |
| =4 | astro | 1.535 | 4.5% | 1.486–1.669 |
| =4 | vuepress | 1.612 | 7.1% | 1.582–1.835 |
| 6 | middleman | 1.875 | 0.9% | 1.863–1.904 |
| 7 | starlight | 2.839 | 4.7% | 2.814–3.142 |
| 8 | gatsby | 15.007 | 1.2% | 14.822–15.266 |

### P v1 · nf 50, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mdbook | 0.058 | 1.5% | 0.058–0.060 |
| 2 | hugo | 0.113 | 2.1% | 0.110–0.116 |
| 3 | publish | 0.139 | 2.2% | 0.136–0.144 |
| 4 | jigsaw | 0.250 | 1.7% | 0.249–0.260 |
| 5 | pelican | 0.636 | 0.3% | 0.634–0.639 |
| 6 | lektor | 0.768 | 2.1% | 0.742–0.779 |
| 7 | eleventy | 0.798 | 0.4% | 0.792–0.800 |
| 8 | nanoc | 1.213 | 1.6% | 1.207–1.254 |
| 9 | sphinx | 3.619 | 0.7% | 3.599–3.663 |
| 10 | sveltekit | 5.419 | 1.8% | 5.341–5.587 |
| 11 | observable-framework | 5.773 | 1.6% | 5.667–5.902 |
| 12 | nextjs-export | 6.254 | 0.6% | 6.220–6.326 |
| 13 | analog | 7.044 | 0.8% | 6.961–7.112 |
| 14 | nuxt-content | 7.627 | 0.7% | 7.617–7.740 |
| 15 | nextra | 25.085 | 1.2% | 24.812–25.506 |
| 16 | dumi | 25.935 | 0.8% | 25.752–26.292 |

### P v1 · nf 50, cs 5 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-nunjucks | 0.249 | 3.3% | 0.243–0.265 |
| 2 | hexo | 1.062 | 0.8% | 1.048–1.070 |

### P v1 · nf 50, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | mkdocs | 0.406 | 2.1% | 0.395–0.416 |
| 2 | docfx | 0.985 | 0.7% | 0.977–0.993 |
| 3 | nikola-mako | 4.814 | 0.3% | 4.789–4.819 |
| 4 | docusaurus | 14.325 | 1.1% | 14.045–14.379 |

### P v1 · nf 50, cs 5 · profile core · fingerprint 90616b2b906d

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 0.749 | 3.7% | 0.720–0.791 |

### P v1 · nf 50, cs 5 · profile core · fingerprint de731ab3b8a5

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zensical | 1.799 | 0.4% | 1.791–1.805 |

### P v1 · nf 50, cs 5 · profile core · fingerprint d9fc9f362ed7

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | vitepress | 1.947 | 5.3% | 1.911–2.176 |

### P v1 · nf 50, cs 5 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | quartz | 2.677 | 0.6% | 2.659–2.701 |

### P v1 · nf 50, cs 5 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | quarto | 40.230 | 0.6% | 39.843–40.374 |

## Caveats

- T5: at 100 files or fewer, bundler-dominated JavaScript generators (Gatsby, Next.js, Astro, VitePress) mostly measure bundler start-up, not content handling. Read the full matrix and the scaling exponent; never quote one small cell as the result.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

None.
