# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:17:02 UTC
- Completed: 2026-10-05 14:24:16 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: P v1 · cell 2/2 (nf 50, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 50 | 50 | 5 | 0.157 | 0.001 | 0.157 | 0.157 | 0.158 | ok | 1 | 0.4% | 317.7 | 16.3 | 3.05 | 68.4 | 4.4 / 54 | 25.2 |
| metalsmith-nunjucks | javascript | 50 | 50 | 5 | 0.425 | 0.008 | 0.430 | 0.415 | 0.431 | ok | 1 | 1.8% | 116.3 | 6.0 | 1.51 | 123.2 | 4.3 / 52 | 34.5 |
| hugo | go | 50 | 50 | 5 | 0.546 | 0.006 | 0.545 | 0.541 | 0.554 | ok | 1 | 1.1% | 91.7 | 4.7 | 3.63 | 263.0 | 5.7 / 53 | 33.1 |
| metalsmith-handlebars | javascript | 50 | 50 | 5 | 0.805 | 0.043 | 0.811 | 0.750 | 0.850 | ok | 1 | 5.4% | 61.7 | 3.2 | 1.45 | 126.3 | 4.3 / 52 | 43.6 |
| eleventy | javascript | 50 | 50 | 5 | 1.236 | 0.018 | 1.226 | 1.221 | 1.260 | ok | 2 | 1.5% | 40.8 | 2.1 | 1.52 | 298.6 | 4.1 / 51 | 33.4 |
| jigsaw | php | 50 | 50 | 5 | 1.297 | 0.008 | 1.296 | 1.289 | 1.310 | ok | 1 | 0.6% | 38.6 | 2.0 | 1.00 | 47.5 | 4.2 / 53 | 71.4 |
| hexo | javascript | 50 | 50 | 5 | 1.935 | 0.021 | 1.930 | 1.916 | 1.960 | ok | 2 | 1.1% | 25.9 | 1.3 | 1.35 | 436.8 | 6.2 / 51 | 44.0 |
| pelican | python | 50 | 50 | 5 | 1.984 | 0.032 | 1.979 | 1.950 | 2.030 | ok | 1 | 1.6% | 25.3 | 1.3 | 1.00 | 46.4 | 3.6 / 51 | 43.3 |
| astro | javascript | 50 | 50 | 5 | 2.682 | 0.140 | 2.605 | 2.575 | 2.901 | ok | 3 | 5.2% | 19.2 | 1.0 | 1.47 | 902.8 | 5.1 / 51 | 65.1 |
| jekyll | ruby | 50 | 50 | 5 | 3.219 | 0.039 | 3.206 | 3.181 | 3.265 | ok | 3 | 1.2% | 15.6 | 0.8 | 1.00 | 111.0 | 5.5 / 51 | 63.4 |
| middleman | ruby | 50 | 50 | 5 | 4.133 | 0.022 | 4.137 | 4.096 | 4.152 | ok | 2 | 0.5% | 12.1 | 0.6 | 2.95 | 100.4 | 4.9 / 52 | 109.2 |
| nanoc | ruby | 50 | 50 | 5 | 4.837 | 0.050 | 4.825 | 4.768 | 4.901 | ok | 4 | 1.0% | 10.4 | 0.5 | 1.00 | 109.1 | 4.9 / 51 | 40.3 |
| mkdocs | python | 50 | 50 | 5 | 5.182 | 0.024 | 5.180 | 5.154 | 5.218 | ok | 5 | 0.5% | 9.7 | 0.5 | 1.00 | 55.4 | 4.4 / 51 | 48.2 |
| vitepress | javascript | 50 | 50 | 5 | 6.257 | 0.219 | 6.355 | 5.885 | 6.420 | ok | 1 | 3.5% | 7.9 | 0.4 | 1.47 | 1136.1 | 14.2 / 162 | 49.1 |
| nextjs-export | javascript | 50 | 50 | 5 | 7.135 | 0.103 | 7.078 | 7.050 | 7.257 | ok | 6 | 1.4% | 7.1 | 0.4 | 3.15 | 1392.6 | 25.2 / 271 | 52.9 |
| nikola-mako | python | 50 | 50 | 5 | 11.783 | 0.062 | 11.752 | 11.727 | 11.860 | ok | 1 | 0.5% | 4.3 | 0.2 | 0.66 | 68.5 | 4.4 / 75 | 52.4 |
| gatsby | javascript | 50 | 50 | 5 | 23.356 | 0.436 | 23.395 | 22.824 | 23.893 | ok | 1 | 1.9% | 2.1 | 0.1 | 1.62 | 821.8 | 9.6 / 130 | 207.8 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### P v1 · nf 50, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 0.157 | 0.4% | 0.157–0.158 |
| 2 | eleventy | 1.226 | 1.5% | 1.221–1.260 |
| 3 | astro | 2.605 | 5.2% | 2.575–2.901 |
| 4 | nanoc | 4.825 | 1.0% | 4.768–4.901 |
| 5 | mkdocs | 5.180 | 0.5% | 5.154–5.218 |
| 6 | nextjs-export | 7.078 | 1.4% | 7.050–7.257 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 90616b2b906d

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-nunjucks | 0.430 | 1.8% | 0.415–0.431 |

### P v1 · nf 50, cs 50 · profile core · fingerprint e2d6f2db677c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 0.545 | 1.1% | 0.541–0.554 |
| 2 | middleman | 4.137 | 0.5% | 4.096–4.152 |

### P v1 · nf 50, cs 50 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 0.811 | 5.4% | 0.750–0.850 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 1.296 | 0.6% | 1.289–1.310 |
| 2 | hexo | 1.930 | 1.1% | 1.916–1.960 |
| 3 | jekyll | 3.206 | 1.2% | 3.181–3.265 |

### P v1 · nf 50, cs 50 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 1.979 | 1.6% | 1.950–2.030 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | vitepress | 6.355 | 3.5% | 5.885–6.420 |

### P v1 · nf 50, cs 50 · profile core · fingerprint c5ccc7094d75

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nikola-mako | 11.752 | 0.5% | 11.727–11.860 |

### P v1 · nf 50, cs 50 · profile core · fingerprint 32b3f23116a6

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | gatsby | 23.395 | 1.9% | 22.824–23.893 |

## Caveats

- T5: at 100 files or fewer, bundler-dominated JavaScript generators (Gatsby, Next.js, Astro, VitePress) mostly measure bundler start-up, not content handling. Read the full matrix and the scaling exponent; never quote one small cell as the result.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

None.
