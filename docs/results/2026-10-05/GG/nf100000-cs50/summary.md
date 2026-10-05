# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-05 14:39:24 UTC
- Completed: 2026-10-05 19:47:40 UTC
- Commit: 6735176945599059d76c29e2692bcdc20e82b911

Suite: GG v1 · cell 2/2 (nf 100000, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pelican | python | 100000 | 50 | 1 | 4805.391 | — | 4805.391 | 4805.391 | 4805.391 | ok | 1 | — | 20.8 | 1.1 | 0.98 | 7534.4 | 7224.4 / 100001 | 42.5 |
| astro | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 44.3 |
| eleventy | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 32.1 |
| gatsby | javascript | 100000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 223.7 |
| hexo | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 39.0 |
| hugo | go | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 27.1 |
| jekyll | ruby | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 46.3 |
| jigsaw | php | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 83.8 |
| metalsmith-handlebars | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 35.9 |
| metalsmith-nunjucks | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 40.2 |
| middleman | ruby | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 101.1 |
| mkdocs | python | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 46.1 |
| nanoc | ruby | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 35.7 |
| nextjs-export | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 48.2 |
| nikola-mako | python | 100000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 49.9 |
| vitepress | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 40.7 |
| zola | rust | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 30.7 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### GG v1 · nf 100000, cs 50 · profile core · fingerprint fe92e3e10f7a

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | pelican | 4805.391 | — | 4805.391–4805.391 |

## Caveats

- T9: oom means the generator exceeded the container memory limit, which is the same for every generator; it is an outcome, not a time.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

- astro (failed): SSGBERK_VERIFY_FAIL build exited 134
- eleventy (failed): SSGBERK_VERIFY_FAIL build exited 134
- gatsby (timeout): timeout
- hexo (failed): SSGBERK_VERIFY_FAIL build exited 134
- hugo (oom): oom
- jekyll (oom): oom
- jigsaw (oom): oom
- metalsmith-handlebars (failed): SSGBERK_VERIFY_FAIL build exited 1
- metalsmith-nunjucks (failed): SSGBERK_VERIFY_FAIL build exited 1
- middleman (oom): oom
- mkdocs (oom): oom
- nanoc (oom): oom
- nextjs-export (oom): oom
- nikola-mako (timeout): timeout
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
- zola (oom): oom
