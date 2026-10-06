# GitHub Actions ubuntu-24.04, one runner per generator

- Environment: GitHub Actions ubuntu-24.04, one runner per generator
- Started: 2026-10-06 14:32:57 UTC
- Completed: 2026-10-06 21:43:51 UTC
- Commit: 4818dd2d1738f4f837fa5d80799b0beef5a92605

Suite: GG v1 · cell 2/2 (nf 100000, cs 50) · profile core · resources 4 CPU / 8.0 GB

| Framework | Language | Files | Size (KB) | Min runs | Mean (s) | Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV | Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) | Image build (s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| hugo | go | 100000 | 50 | 1 | 1131.006 | — | 1131.006 | 1131.006 | 1131.006 | ok | 1 | — | 88.4 | 4.5 | 3.68 | 7344.4 | 11437.3 / 100003 | 30.7 |
| lektor | python | 100000 | 50 | 1 | 6644.824 | — | 6644.824 | 6644.824 | 6644.824 | ok | 2 | — | 15.0 | 0.8 | 0.97 | 7136.9 | 8112.4 / 100004 | 52.1 |
| pelican | python | 100000 | 50 | 1 | 7845.090 | — | 7845.090 | 7845.090 | 7845.090 | ok | 3 | — | 12.7 | 0.7 | 0.99 | 7534.6 | 7224.4 / 100001 | 53.3 |
| analog | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 59.1 |
| astro | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 48.9 |
| docfx | c# | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 66.9 |
| docusaurus | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 98.5 |
| dumi | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 79.5 |
| eleventy | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 51.1 |
| gatsby | javascript | 100000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 235.2 |
| hakyll | haskell | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 2686.1 |
| hexo | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 50.0 |
| jekyll | ruby | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 50.3 |
| jigsaw | php | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 64.5 |
| mdbook | rust | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 25.9 |
| metalsmith-handlebars | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 36.0 |
| metalsmith-nunjucks | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 32.5 |
| middleman | ruby | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 104.0 |
| mkdocs | python | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 44.8 |
| nanoc | ruby | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 41.6 |
| nextjs-export | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 57.1 |
| nextra | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 77.6 |
| nikola-mako | python | 100000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 68.0 |
| nuxt-content | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 58.5 |
| observable-framework | javascript | 100000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 42.2 |
| publish | swift | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 118.3 |
| quarto | typescript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 37.8 |
| quartz | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 265.3 |
| sphinx | python | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 46.9 |
| starlight | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 50.4 |
| sveltekit | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 39.9 |
| vitepress | javascript | 100000 | 50 | — | — | — | — | — | — | failed | — | — | — | — | — | — | — | 40.9 |
| vuepress | javascript | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 38.6 |
| zensical | python | 100000 | 50 | — | — | — | — | — | — | timeout | — | — | — | — | — | — | — | 57.5 |
| zola | rust | 100000 | 50 | — | — | — | — | — | — | oom | — | — | — | — | — | — | — | 23.7 |

## Ranking

Ordered by median; generators whose min–max ranges overlap share a rank (`=n`). Only results of the same suite, cell, profile, fingerprint and feature set are ranked together.

### GG v1 · nf 100000, cs 50 · profile core · fingerprint 3f2f1aaf006c

| Rank | Framework | Median (s) | CV | Min–Max (s) |
|---|---|---|---|---|
| 1 | hugo | 1131.006 | — | 1131.006–1131.006 |
| 2 | lektor | 6644.824 | — | 6644.824–6644.824 |
| 3 | pelican | 7845.090 | — | 7845.090–7845.090 |

## Caveats

- T9: oom means the generator exceeded the container memory limit, which is the same for every generator; it is an outcome, not a time.
- T7: peak RSS is the largest single process, not the sum, so it under-reports multi-process generators.

## Failed / timeout / oom / nonconformant / unsupported

- analog (oom): oom
- astro (failed): SSGBERK_VERIFY_FAIL build exited 134
- docfx (failed): SSGBERK_VERIFY_FAIL build exited 255
- docusaurus (failed): SSGBERK_VERIFY_FAIL build exited 1
- dumi (failed): SSGBERK_VERIFY_FAIL build exited 134
- eleventy (oom): oom
- gatsby (timeout): timeout
- hakyll (failed)
- hexo (oom): oom
- jekyll (oom): oom
- jigsaw (oom): oom
- mdbook (oom): oom
- metalsmith-handlebars (failed): SSGBERK_VERIFY_FAIL build exited 1
- metalsmith-nunjucks (failed): SSGBERK_VERIFY_FAIL build exited 1
- middleman (oom): oom
- mkdocs (oom): oom
- nanoc (oom): oom
- nextjs-export (failed)
- nextra (oom): oom
- nikola-mako (timeout): timeout
- nuxt-content (failed): SSGBERK_VERIFY_FAIL build exited 134
- observable-framework (timeout): timeout
- publish (oom): oom
- quarto (oom): oom
- quartz (oom): oom
- sphinx (oom): oom
- starlight (failed): SSGBERK_VERIFY_FAIL build exited 134
- sveltekit (oom): oom
- vitepress (failed): SSGBERK_VERIFY_FAIL build exited 134
- vuepress (oom): oom
- zensical (timeout): timeout
- zola (oom): oom
