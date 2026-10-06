# Benchmark rounds 2026-10-06: suites P and M, 35 generators

First rounds with all 35 generators (the 17 of 2026-10-05 plus the 18 of ssg-frameworks spec 007) on GitHub Actions (`ubuntu-24.04` hosted runners, one runner per generator and cell, `--cpus 4 --memory 8g`, profile `core`, Node generators with `--max-old-space-size=6144`).

| Suite | Pages | Sizes | Workflow run | Files |
|---|---|---|---|---|
| P (website pessoal) | 50 | 5 KB, 50 KB | [37454064173](https://github.com/ssgberk/benchmark-tool/actions/runs/37454064173) | [P/](./P/) |
| M (site corporativo) | 1,000 | 5 KB, 50 KB | [37454077632](https://github.com/ssgberk/benchmark-tool/actions/runs/37454077632) | [M/](./M/) |

## Caveats

- **Rankings are per runner.** Hosted runners differ in CPU model, so the per-cell `summary.md` ranks only generators that shared a runner fingerprint. The tables below show medians side by side for reading.
- **Node heap.** Every Node generator runs with a 6 GB V8 heap cap (spec 008 decision 6). At 1,000 × 50 KB, vitepress, docusaurus and dumi still exceed it (exit 134; vitepress reached ~6,040 MB), and nextra and quartz hit the 8 GB container limit.
- **quarto** timed out at 1,000 × 50 KB.

## P: 50 pages

### 50 pages × 5 KB (35/35 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 0.032 | 1.0% | 1,551 | 34 |
| mdbook | rust | 0.058 | 1.5% | 862 | 17 |
| hugo | go | 0.113 | 2.1% | 443 | 87 |
| publish | swift | 0.139 | 2.2% | 358 | 31 |
| metalsmith-nunjucks | javascript | 0.249 | 3.3% | 201 | 86 |
| jigsaw | php | 0.250 | 1.7% | 200 | 41 |
| metalsmith-handlebars | javascript | 0.269 | 2.6% | 186 | 91 |
| mkdocs | python | 0.406 | 2.1% | 123 | 33 |
| pelican | python | 0.636 | 0.3% | 79 | 42 |
| jekyll | ruby | 0.749 | 3.7% | 67 | 81 |
| lektor | python | 0.768 | 2.1% | 65 | 48 |
| eleventy | javascript | 0.798 | 0.4% | 63 | 134 |
| docfx | c# | 0.985 | 0.7% | 51 | 133 |
| hexo | javascript | 1.062 | 0.8% | 47 | 149 |
| hakyll | haskell | 1.066 | 1.7% | 47 | 318 |
| nanoc | ruby | 1.213 | 1.6% | 41 | 75 |
| astro | javascript | 1.535 | 4.5% | 33 | 613 |
| vuepress | javascript | 1.612 | 7.1% | 31 | 503 |
| zensical | python | 1.799 | 0.4% | 28 | 70 |
| middleman | ruby | 1.875 | 0.9% | 27 | 97 |
| vitepress | javascript | 1.947 | 5.3% | 26 | 453 |
| quartz | javascript | 2.677 | 0.6% | 19 | 453 |
| starlight | javascript | 2.839 | 4.7% | 18 | 835 |
| sphinx | python | 3.619 | 0.7% | 14 | 100 |
| nikola-mako | python | 4.814 | 0.3% | 10 | 64 |
| sveltekit | javascript | 5.419 | 1.8% | 9 | 732 |
| observable-framework | javascript | 5.773 | 1.6% | 9 | 607 |
| nextjs-export | javascript | 6.254 | 0.6% | 8 | 1,383 |
| analog | javascript | 7.044 | 0.8% | 7 | 1,652 |
| nuxt-content | javascript | 7.627 | 0.7% | 7 | 1,124 |
| docusaurus | javascript | 14.3 | 1.1% | 3 | 1,799 |
| gatsby | javascript | 15.0 | 1.2% | 3 | 709 |
| nextra | javascript | 25.1 | 1.2% | 2 | 1,777 |
| dumi | javascript | 25.9 | 0.8% | 2 | 1,585 |
| quarto | typescript | 40.2 | 0.6% | 1 | 410 |

### 50 pages × 50 KB (35/35 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 0.157 | 1.7% | 319 | 68 |
| mdbook | rust | 0.228 | 2.8% | 219 | 84 |
| hugo | go | 0.551 | 1.1% | 91 | 269 |
| metalsmith-nunjucks | javascript | 0.733 | 2.7% | 68 | 149 |
| eleventy | javascript | 0.772 | 1.7% | 65 | 298 |
| metalsmith-handlebars | javascript | 0.773 | 1.3% | 65 | 124 |
| publish | swift | 0.998 | 0.4% | 50 | 36 |
| jigsaw | php | 1.336 | 0.2% | 37 | 48 |
| hexo | javascript | 2.075 | 3.5% | 24 | 438 |
| astro | javascript | 2.512 | 0.7% | 20 | 883 |
| pelican | python | 2.628 | 1.3% | 19 | 46 |
| nanoc | ruby | 2.638 | 2.5% | 19 | 109 |
| lektor | python | 3.144 | 1.3% | 16 | 57 |
| jekyll | ruby | 3.921 | 0.5% | 13 | 110 |
| middleman | ruby | 3.978 | 0.8% | 13 | 100 |
| vuepress | javascript | 4.503 | 1.9% | 11 | 1,237 |
| starlight | javascript | 4.970 | 0.8% | 10 | 1,406 |
| mkdocs | python | 5.116 | 1.3% | 10 | 56 |
| hakyll | haskell | 5.545 | 8.8% | 9 | 946 |
| nextjs-export | javascript | 5.797 | 4.0% | 9 | 1,384 |
| analog | javascript | 6.659 | 0.9% | 8 | 1,842 |
| docfx | c# | 6.822 | 6.8% | 7 | 500 |
| vitepress | javascript | 7.537 | 1.5% | 7 | 1,121 |
| nikola-mako | python | 8.838 | 0.9% | 6 | 67 |
| zensical | python | 13.9 | 0.6% | 4 | 140 |
| quartz | javascript | 15.0 | 1.0% | 3 | 802 |
| nuxt-content | javascript | 20.7 | 0.9% | 2 | 1,600 |
| observable-framework | javascript | 24.8 | 0.8% | 2 | 772 |
| sveltekit | javascript | 27.0 | 0.5% | 2 | 958 |
| gatsby | javascript | 28.4 | 3.4% | 2 | 909 |
| sphinx | python | 31.3 | 1.7% | 2 | 437 |
| nextra | javascript | 54.5 | 1.3% | 1 | 3,134 |
| quarto | typescript | 98.6 | 0.3% | 1 | 985 |
| docusaurus | javascript | 129.9 | 0.7% | 0 | 4,236 |
| dumi | javascript | 151.5 | 0.7% | 0 | 3,487 |

## M: 1,000 pages

### 1,000 pages × 5 KB (35/35 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 0.287 | 2.0% | 3,489 | 103 |
| metalsmith-handlebars | javascript | 1.009 | 1.7% | 991 | 207 |
| metalsmith-nunjucks | javascript | 1.140 | 1.4% | 877 | 204 |
| hugo | go | 1.162 | 1.6% | 860 | 487 |
| jekyll | ruby | 1.267 | 0.9% | 789 | 106 |
| eleventy | javascript | 2.167 | 3.6% | 461 | 336 |
| hexo | javascript | 2.511 | 2.6% | 398 | 723 |
| publish | swift | 2.540 | 0.4% | 394 | 54 |
| jigsaw | php | 2.658 | 0.3% | 376 | 75 |
| astro | javascript | 3.613 | 2.6% | 277 | 819 |
| mdbook | rust | 3.709 | 0.5% | 270 | 170 |
| pelican | python | 6.775 | 0.5% | 148 | 51 |
| starlight | javascript | 8.054 | 0.6% | 124 | 1,105 |
| docfx | c# | 8.671 | 1.2% | 115 | 220 |
| lektor | python | 8.887 | 0.5% | 113 | 73 |
| nextjs-export | javascript | 9.290 | 6.4% | 108 | 1,424 |
| mkdocs | python | 9.370 | 1.2% | 107 | 59 |
| middleman | ruby | 9.482 | 0.9% | 105 | 124 |
| vuepress | javascript | 9.573 | 1.4% | 104 | 2,131 |
| nanoc | ruby | 9.725 | 0.9% | 103 | 157 |
| hakyll | haskell | 11.5 | 0.8% | 87 | 549 |
| vitepress | javascript | 16.3 | 0.5% | 61 | 1,826 |
| analog | javascript | 19.0 | 1.7% | 53 | 2,724 |
| quartz | javascript | 23.6 | 0.3% | 42 | 2,267 |
| nikola-mako | python | 24.6 | 1.2% | 41 | 101 |
| zensical | python | 32.8 | 1.0% | 30 | 220 |
| sveltekit | javascript | 35.1 | 1.0% | 28 | 1,399 |
| gatsby | javascript | 35.9 | 0.7% | 28 | 789 |
| nuxt-content | javascript | 40.9 | 2.0% | 24 | 1,809 |
| sphinx | python | 54.5 | 0.7% | 18 | 761 |
| nextra | javascript | 90.6 | 0.6% | 11 | 6,228 |
| observable-framework | javascript | 116.5 | 0.6% | 9 | 646 |
| docusaurus | javascript | 255.2 | 1.6% | 4 | 6,388 |
| quarto | typescript | 560.8 | 3.0% | 2 | 940 |
| dumi | javascript | 677.5 | 1.4% | 1 | 4,836 |

### 1,000 pages × 50 KB (29/35 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 2.599 | 0.7% | 385 | 641 |
| jekyll | ruby | 3.740 | 1.0% | 267 | 272 |
| mdbook | rust | 6.151 | 1.2% | 163 | 1,506 |
| eleventy | javascript | 6.387 | 0.5% | 157 | 1,117 |
| metalsmith-handlebars | javascript | 9.338 | 1.0% | 107 | 551 |
| astro | javascript | 9.463 | 0.6% | 106 | 1,346 |
| metalsmith-nunjucks | javascript | 9.468 | 2.8% | 106 | 563 |
| hugo | go | 9.791 | 1.2% | 102 | 3,900 |
| hexo | javascript | 14.9 | 2.3% | 67 | 3,439 |
| nextjs-export | javascript | 16.4 | 4.2% | 61 | 1,418 |
| jigsaw | php | 19.0 | 0.3% | 53 | 153 |
| publish | swift | 20.3 | 0.8% | 49 | 161 |
| starlight | javascript | 34.7 | 0.6% | 29 | 2,488 |
| pelican | python | 49.3 | 0.7% | 20 | 117 |
| middleman | ruby | 52.2 | 1.3% | 19 | 186 |
| lektor | python | 60.0 | 1.3% | 17 | 153 |
| nanoc | ruby | 68.4 | 1.0% | 15 | 481 |
| hakyll | haskell | 82.0 | 6.1% | 12 | 2,581 |
| mkdocs | python | 104.8 | 0.6% | 10 | 286 |
| vuepress | javascript | 105.7 | 15.1% | 9 | 8,373 |
| analog | javascript | 108.8 | 1.8% | 9 | 4,679 |
| docfx | c# | 116.4 | 0.7% | 9 | 877 |
| nikola-mako | python | 159.6 | 1.0% | 6 | 102 |
| gatsby | javascript | 217.8 | 1.1% | 5 | 1,138 |
| zensical | python | 312.5 | 0.2% | 3 | 1,337 |
| sveltekit | javascript | 335.2 | 0.5% | 3 | 4,583 |
| nuxt-content | javascript | 354.7 | 2.4% | 3 | 5,982 |
| observable-framework | javascript | 585.6 | 0.7% | 2 | 1,243 |
| sphinx | python | 805.5 | 2.9% | 1 | 7,212 |

Failed: docusaurus (Node heap out of memory, exit 134); dumi (Node heap out of memory, exit 134); nextra (8 GB memory limit); quarto (timeout); quartz (8 GB memory limit); vitepress (Node heap out of memory, exit 134).
