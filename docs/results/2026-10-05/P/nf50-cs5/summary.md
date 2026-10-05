# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:17:02 UTC
- Completed: 2026-10-05 14:23:15 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: P v1 · cell 1/2 (nf 50, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 50 | 5 | 5 | 0.026 | 0.000 | 0.026 | 0.025 | 0.026 | ok | 1 | 1.9% | 1941.7 | 10.4 | 1.57 | 33.7 | 0.5 / 54 | 30.1 |
| hugo | go | 50 | 5 | 5 | 0.112 | 0.001 | 0.111 | 0.111 | 0.113 | ok | 1 | 1.0% | 450.0 | 2.4 | 2.75 | 85.6 | 0.6 / 53 | 24.5 |
| jigsaw | php | 50 | 5 | 5 | 0.157 | 0.001 | 0.156 | 0.156 | 0.159 | ok | 1 | 0.8% | 319.8 | 1.7 | 0.99 | 41.0 | 0.5 / 53 | 73.8 |
| metalsmith-handlebars | javascript | 50 | 5 | 5 | 0.216 | 0.003 | 0.216 | 0.213 | 0.220 | ok | 1 | 1.4% | 231.3 | 1.2 | 1.57 | 90.4 | 0.4 / 52 | 45.8 |
| metalsmith-nunjucks | javascript | 50 | 5 | 5 | 0.250 | 0.003 | 0.249 | 0.247 | 0.255 | ok | 2 | 1.3% | 200.6 | 1.1 | 1.49 | 85.8 | 0.4 / 52 | 30.8 |
| pelican | python | 50 | 5 | 5 | 0.634 | 0.003 | 0.632 | 0.630 | 0.638 | ok | 3 | 0.5% | 79.1 | 0.4 | 1.00 | 42.1 | 0.4 / 51 | 55.7 |
| mkdocs | python | 50 | 5 | 5 | 0.713 | 0.012 | 0.711 | 0.701 | 0.733 | ok | 4 | 1.7% | 70.4 | 0.4 | 1.00 | 33.1 | 0.5 / 51 | 46.0 |
| eleventy | javascript | 50 | 5 | 5 | 0.718 | 0.003 | 0.719 | 0.712 | 0.720 | ok | 1 | 0.5% | 69.5 | 0.4 | 1.42 | 134.0 | 0.4 / 51 | 38.0 |
| hexo | javascript | 50 | 5 | 5 | 1.005 | 0.005 | 1.005 | 0.999 | 1.010 | ok | 5 | 0.5% | 49.8 | 0.3 | 1.38 | 150.1 | 0.6 / 51 | 40.8 |
| jekyll | ruby | 50 | 5 | 5 | 1.156 | 0.009 | 1.155 | 1.146 | 1.171 | ok | 6 | 0.8% | 43.3 | 0.2 | 1.00 | 80.8 | 0.6 / 51 | 56.7 |
| nanoc | ruby | 50 | 5 | 5 | 1.326 | 0.020 | 1.321 | 1.306 | 1.358 | ok | 7 | 1.5% | 37.8 | 0.2 | 1.00 | 75.4 | 0.5 / 51 | 46.1 |
| middleman | ruby | 50 | 5 | 5 | 1.721 | 0.029 | 1.725 | 1.685 | 1.764 | ok | 2 | 1.7% | 29.0 | 0.2 | 1.71 | 97.1 | 0.5 / 52 | 107.7 |
| astro | javascript | 50 | 5 | 5 | 2.082 | 0.071 | 2.061 | 2.014 | 2.186 | ok | 8 | 3.4% | 24.3 | 0.1 | 1.44 | 621.2 | 0.5 / 51 | 43.9 |
| vitepress | javascript | 50 | 5 | 5 | 2.826 | 0.122 | 2.783 | 2.719 | 3.025 | ok | 1 | 4.3% | 18.0 | 0.1 | 1.61 | 461.3 | 1.8 / 162 | 43.3 |
| nikola-mako | python | 50 | 5 | 5 | 5.499 | 0.029 | 5.502 | 5.463 | 5.534 | ok | 9 | 0.5% | 9.1 | 0.0 | 0.27 | 62.2 | 0.7 / 75 | 52.5 |
| nextjs-export | javascript | 50 | 5 | 5 | 6.377 | 0.145 | 6.369 | 6.227 | 6.537 | ok | 10 | 2.3% | 7.9 | 0.0 | 3.13 | 1489.7 | 3.9 / 271 | 61.5 |
| gatsby | javascript | 50 | 5 | 5 | 21.491 | 0.112 | 21.492 | 21.383 | 21.671 | ok | 11 | 0.5% | 2.3 | 0.0 | 1.72 | 679.8 | 2.1 / 130 | 239.6 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### P v1 · nf 50, cs 5 · profile core · fingerprint 18989d6c17f3

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 0.026 | 1.9% | 0.025–0.026 |

### P v1 · nf 50, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 0.111 | 1.0% | 0.111–0.113 |
| 2 | metalsmith-nunjucks | 0.249 | 1.3% | 0.247–0.255 |
| 3 | pelican | 0.632 | 0.5% | 0.630–0.638 |
| 4 | mkdocs | 0.711 | 1.7% | 0.701–0.733 |
| 5 | hexo | 1.005 | 0.5% | 0.999–1.010 |
| 6 | jekyll | 1.155 | 0.8% | 1.146–1.171 |
| 7 | nanoc | 1.321 | 1.5% | 1.306–1.358 |
| 8 | astro | 2.061 | 3.4% | 2.014–2.186 |
| 9 | nikola-mako | 5.502 | 0.5% | 5.463–5.534 |
| 10 | nextjs-export | 6.369 | 2.3% | 6.227–6.537 |
| 11 | gatsby | 21.492 | 0.5% | 21.383–21.671 |

### P v1 · nf 50, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jigsaw | 0.156 | 0.8% | 0.156–0.159 |

### P v1 · nf 50, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 0.216 | 1.4% | 0.213–0.220 |
| 2 | middleman | 1.725 | 1.7% | 1.685–1.764 |

### P v1 · nf 50, cs 5 · profile core · fingerprint c5ccc7094d75

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | eleventy | 0.719 | 0.5% | 0.712–0.720 |

### P v1 · nf 50, cs 5 · profile core · fingerprint 9c2b3f048b3b

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | vitepress | 2.783 | 4.3% | 2.719–3.025 |

## Caveats

- T5: at 100 files or fewer, bundler-dominated JavaScript generators (Gatsby, Next.js, Astro, VitePress) mostly measure bundler start-up, not content handling. Read the full matrix and the scaling exponent; never quote one small cell as the result.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

None.
