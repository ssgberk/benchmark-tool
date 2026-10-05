# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:26:00 UTC
- Completed: 2026-10-05 14:33:16 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: M v1 · cell 1/2 (nf 1000, cs 5) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zola | rust | 1000 | 5 | 5 | 0.190 | 0.002 | 0.191 | 0.188 | 0.192 | ok | 1 | 0.9% | 5233.2 | 28.0 | 2.49 | 103.0 | 8.9 / 1004 | 26.4 |
| metalsmith-nunjucks | javascript | 1000 | 5 | 5 | 0.924 | 0.022 | 0.925 | 0.889 | 0.943 | ok | 1 | 2.3% | 1081.3 | 5.8 | 1.59 | 205.3 | 8.9 / 1002 | 31.2 |
| hugo | go | 1000 | 5 | 5 | 1.280 | 0.018 | 1.282 | 1.252 | 1.302 | ok | 1 | 1.4% | 780.0 | 4.2 | 3.60 | 472.6 | 12.3 / 1003 | 24.1 |
| jekyll | ruby | 1000 | 5 | 5 | 1.373 | 0.022 | 1.383 | 1.342 | 1.397 | ok | 1 | 1.6% | 723.2 | 3.9 | 1.00 | 105.1 | 11.2 / 1001 | 56.5 |
| eleventy | javascript | 1000 | 5 | 5 | 1.683 | 0.059 | 1.652 | 1.645 | 1.785 | ok | 1 | 3.5% | 605.2 | 3.2 | 1.45 | 343.2 | 8.3 / 1001 | 42.1 |
| metalsmith-handlebars | javascript | 1000 | 5 | 5 | 1.859 | 0.027 | 1.846 | 1.838 | 1.903 | ok | 1 | 1.5% | 541.8 | 2.9 | 1.50 | 284.9 | 8.9 / 1002 | 32.2 |
| jigsaw | php | 1000 | 5 | 5 | 2.693 | 0.021 | 2.693 | 2.667 | 2.716 | ok | 2 | 0.8% | 371.3 | 2.0 | 1.00 | 75.1 | 9.3 / 1003 | 76.9 |
| hexo | javascript | 1000 | 5 | 5 | 3.227 | 0.015 | 3.235 | 3.207 | 3.241 | ok | 2 | 0.4% | 309.1 | 1.6 | 1.50 | 722.0 | 12.5 / 1001 | 43.7 |
| astro | javascript | 1000 | 5 | 5 | 3.902 | 0.129 | 3.861 | 3.812 | 4.129 | ok | 2 | 3.3% | 259.0 | 1.4 | 1.45 | 821.7 | 10.4 / 1001 | 44.3 |
| pelican | python | 1000 | 5 | 5 | 7.744 | 0.032 | 7.752 | 7.708 | 7.776 | ok | =3 | 0.4% | 129.0 | 0.7 | 1.00 | 51.5 | 7.4 / 1001 | 44.3 |
| mkdocs | python | 1000 | 5 | 5 | 7.810 | 0.066 | 7.822 | 7.729 | 7.896 | ok | =3 | 0.8% | 127.8 | 0.7 | 1.00 | 59.2 | 9.0 / 1001 | 46.5 |
| nextjs-export | javascript | 1000 | 5 | 5 | 8.735 | 0.121 | 8.752 | 8.614 | 8.906 | ok | 2 | 1.4% | 114.3 | 0.6 | 3.13 | 1374.8 | 65.6 / 5021 | 46.3 |
| middleman | ruby | 1000 | 5 | 5 | 9.736 | 0.066 | 9.739 | 9.648 | 9.833 | ok | 2 | 0.7% | 102.7 | 0.5 | 2.85 | 123.6 | 10.0 / 1002 | 105.4 |
| nanoc | ruby | 1000 | 5 | 5 | 10.686 | 0.288 | 10.554 | 10.394 | 11.093 | ok | 3 | 2.7% | 94.8 | 0.5 | 1.00 | 156.7 | 10.1 / 1001 | 52.2 |
| vitepress | javascript | 1000 | 5 | 5 | 14.158 | 0.028 | 14.171 | 14.123 | 14.183 | ok | 2 | 0.2% | 70.6 | 0.4 | 1.49 | 1822.8 | 73.2 / 3012 | 41.9 |
| nikola-mako | python | 1000 | 5 | 5 | 23.925 | 0.110 | 23.943 | 23.793 | 24.062 | ok | 1 | 0.5% | 41.8 | 0.2 | 0.83 | 101.2 | 8.8 / 1025 | 50.1 |
| gatsby | javascript | 1000 | 5 | 5 | 33.537 | 0.618 | 33.450 | 32.844 | 34.216 | ok | 5 | 1.8% | 29.9 | 0.2 | 1.59 | 793.8 | 20.7 / 2030 | 229.1 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### M v1 · nf 1000, cs 5 · profile core · fingerprint ba134637a49c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | zola | 0.191 | 0.9% | 0.188–0.192 |
| 2 | vitepress | 14.171 | 0.2% | 14.123–14.183 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint ebe58c534103

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-nunjucks | 0.925 | 2.3% | 0.889–0.943 |
| 2 | nextjs-export | 8.752 | 1.4% | 8.614–8.906 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 1.282 | 1.4% | 1.252–1.302 |
| 2 | astro | 3.861 | 3.3% | 3.812–4.129 |
| 3 | nanoc | 10.554 | 2.7% | 10.394–11.093 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 8e17af3b158e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | jekyll | 1.383 | 1.6% | 1.342–1.397 |
| 2 | jigsaw | 2.693 | 0.8% | 2.667–2.716 |
| =3 | pelican | 7.752 | 0.4% | 7.708–7.776 |
| =3 | mkdocs | 7.822 | 0.8% | 7.729–7.896 |
| 5 | gatsby | 33.450 | 1.8% | 32.844–34.216 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint 2bb7b205c77e

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | eleventy | 1.652 | 3.5% | 1.645–1.785 |
| 2 | hexo | 3.235 | 0.4% | 3.207–3.241 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint ae30efe0efb4

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | metalsmith-handlebars | 1.846 | 1.5% | 1.838–1.903 |
| 2 | middleman | 9.739 | 0.7% | 9.648–9.833 |

### M v1 · nf 1000, cs 5 · profile core · fingerprint fe502e5b5baa

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | nikola-mako | 23.943 | 0.5% | 23.793–24.062 |

## Failed / timeout / oom / nonconformant / unsupported

None.
