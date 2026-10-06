# Benchmark rounds 2026-10-05: suites P, M, G, GG

First rounds of spec 008 on GitHub Actions (`ubuntu-24.04` hosted runners, one runner per generator and cell, `--cpus 4 --memory 8g`, profile `core`, Node's default heap).

| Suite | Pages | Sizes | Workflow run | Files |
|---|---|---|---|---|
| P (website pessoal) | 50 | 5 KB, 50 KB | [37323370322](https://github.com/ssgberk/benchmark-tool/actions/runs/37323370322) | [P/](./P/) |
| M (site corporativo) | 1,000 | 5 KB, 50 KB | [37324582475](https://github.com/ssgberk/benchmark-tool/actions/runs/37324582475) | [M/](./M/) |
| G (grande portal) | 10,000 | 5 KB, 50 KB | [37324595599](https://github.com/ssgberk/benchmark-tool/actions/runs/37324595599) | [G/](./G/) |
| GG (portal massivo) | 100,000 | 5 KB, 50 KB | [37324607911](https://github.com/ssgberk/benchmark-tool/actions/runs/37324607911) | [GG/](./GG/) |

## Caveats

- **Rankings are per runner.** Hosted runners differ in CPU model, so the per-cell `summary.md` ranks only generators that shared a runner fingerprint (6 fingerprints in P). The tables below show medians side by side for reading, not as a ranking.
- **Node heap.** These rounds used Node's default V8 heap. astro, eleventy, hexo and vitepress failed with `JavaScript heap out of memory` (exit 134) in M/G/GG well below the 8 GB limit. Since spec 008 decision 6 every Node generator runs with `--max-old-space-size=6144`; those cells are re-run in a later round.
- **gatsby, G** was re-run after a stats-parsing bug lost its 10,000 × 5 KB cell (fixed in #16; re-run: workflow run 37364276814, both gatsby G cells replaced).
- **GG 50 KB** is about 5.1 GB of markdown; most generators hit the 8 GB memory limit (`oom`).

## P: 50 pages

### 50 pages × 5 KB (17/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 0.026 | 1.9% | 1,942 | 34 |
| hugo | go | 0.111 | 1.0% | 450 | 86 |
| jigsaw | php | 0.156 | 0.8% | 320 | 41 |
| metalsmith-handlebars | javascript | 0.216 | 1.4% | 231 | 90 |
| metalsmith-nunjucks | javascript | 0.249 | 1.3% | 201 | 86 |
| pelican | python | 0.632 | 0.5% | 79 | 42 |
| mkdocs | python | 0.711 | 1.7% | 70 | 33 |
| eleventy | javascript | 0.719 | 0.5% | 70 | 134 |
| hexo | javascript | 1.005 | 0.5% | 50 | 150 |
| jekyll | ruby | 1.155 | 0.8% | 43 | 81 |
| nanoc | ruby | 1.321 | 1.5% | 38 | 75 |
| middleman | ruby | 1.725 | 1.7% | 29 | 97 |
| astro | javascript | 2.061 | 3.4% | 24 | 621 |
| vitepress | javascript | 2.783 | 4.3% | 18 | 461 |
| nikola-mako | python | 5.502 | 0.5% | 9 | 62 |
| nextjs-export | javascript | 6.369 | 2.3% | 8 | 1,490 |
| gatsby | javascript | 21.5 | 0.5% | 2 | 680 |

### 50 pages × 50 KB (17/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 0.157 | 0.4% | 318 | 68 |
| metalsmith-nunjucks | javascript | 0.430 | 1.8% | 116 | 123 |
| hugo | go | 0.545 | 1.1% | 92 | 263 |
| metalsmith-handlebars | javascript | 0.811 | 5.4% | 62 | 126 |
| eleventy | javascript | 1.226 | 1.5% | 41 | 299 |
| jigsaw | php | 1.296 | 0.6% | 39 | 48 |
| hexo | javascript | 1.930 | 1.1% | 26 | 437 |
| pelican | python | 1.979 | 1.6% | 25 | 46 |
| astro | javascript | 2.605 | 5.2% | 19 | 903 |
| jekyll | ruby | 3.206 | 1.2% | 16 | 111 |
| middleman | ruby | 4.137 | 0.5% | 12 | 100 |
| nanoc | ruby | 4.825 | 1.0% | 10 | 109 |
| mkdocs | python | 5.180 | 0.5% | 10 | 55 |
| vitepress | javascript | 6.355 | 3.5% | 8 | 1,136 |
| nextjs-export | javascript | 7.078 | 1.4% | 7 | 1,393 |
| nikola-mako | python | 11.8 | 0.5% | 4 | 69 |
| gatsby | javascript | 23.4 | 1.9% | 2 | 822 |

## M: 1,000 pages

### 1,000 pages × 5 KB (17/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 0.191 | 0.9% | 5,233 | 103 |
| metalsmith-nunjucks | javascript | 0.925 | 2.3% | 1,081 | 205 |
| hugo | go | 1.282 | 1.4% | 780 | 473 |
| jekyll | ruby | 1.383 | 1.6% | 723 | 105 |
| eleventy | javascript | 1.652 | 3.5% | 605 | 343 |
| metalsmith-handlebars | javascript | 1.846 | 1.5% | 542 | 285 |
| jigsaw | php | 2.693 | 0.8% | 371 | 75 |
| hexo | javascript | 3.235 | 0.4% | 309 | 722 |
| astro | javascript | 3.861 | 3.3% | 259 | 822 |
| pelican | python | 7.752 | 0.4% | 129 | 51 |
| mkdocs | python | 7.822 | 0.8% | 128 | 59 |
| nextjs-export | javascript | 8.752 | 1.4% | 114 | 1,375 |
| middleman | ruby | 9.739 | 0.7% | 103 | 124 |
| nanoc | ruby | 10.6 | 2.7% | 95 | 157 |
| vitepress | javascript | 14.2 | 0.2% | 71 | 1,823 |
| nikola-mako | python | 23.9 | 0.5% | 42 | 101 |
| gatsby | javascript | 33.5 | 1.8% | 30 | 794 |

### 1,000 pages × 50 KB (16/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 2.041 | 1.3% | 490 | 641 |
| jekyll | ruby | 3.016 | 5.4% | 332 | 279 |
| astro | javascript | 5.638 | 1.7% | 177 | 1,385 |
| eleventy | javascript | 8.043 | 0.4% | 124 | 1,105 |
| metalsmith-nunjucks | javascript | 9.517 | 1.6% | 105 | 544 |
| metalsmith-handlebars | javascript | 9.650 | 3.1% | 104 | 544 |
| hugo | go | 9.717 | 1.5% | 103 | 3,865 |
| nextjs-export | javascript | 15.8 | 0.7% | 63 | 1,359 |
| hexo | javascript | 23.2 | 1.3% | 43 | 3,141 |
| jigsaw | php | 25.6 | 0.5% | 39 | 153 |
| middleman | ruby | 32.0 | 3.4% | 31 | 187 |
| nanoc | ruby | 55.1 | 2.6% | 18 | 481 |
| pelican | python | 59.6 | 0.6% | 17 | 118 |
| mkdocs | python | 69.0 | 4.2% | 14 | 286 |
| nikola-mako | python | 158.2 | 8.8% | 6 | 101 |
| gatsby | javascript | 242.2 | 3.4% | 4 | 1,106 |

Failed: vitepress (Node heap out of memory, exit 134).

## G: 10,000 pages

### 10,000 pages × 5 KB (16/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 2.604 | 0.2% | 3,841 | 753 |
| jekyll | ruby | 8.248 | 0.9% | 1,212 | 324 |
| hugo | go | 12.1 | 0.3% | 823 | 3,933 |
| metalsmith-nunjucks | javascript | 12.9 | 0.0% | 774 | 642 |
| metalsmith-handlebars | javascript | 13.7 | 0.8% | 730 | 666 |
| astro | javascript | 14.3 | 1.6% | 699 | 1,333 |
| eleventy | javascript | 18.7 | 0.6% | 535 | 1,304 |
| hexo | javascript | 25.8 | 0.5% | 387 | 3,648 |
| jigsaw | php | 26.7 | 0.4% | 375 | 405 |
| nextjs-export | javascript | 49.5 | 1.3% | 202 | 1,363 |
| mkdocs | python | 66.8 | 0.9% | 150 | 297 |
| pelican | python | 83.9 | 0.7% | 119 | 142 |
| middleman | ruby | 87.9 | 0.7% | 114 | 317 |
| nanoc | ruby | 117.6 | 1.3% | 85 | 632 |
| gatsby | javascript | 145.0 | 6.4% | 69 | 1,658 |
| nikola-mako | python | 218.5 | 1.8% | 46 | 440 |

Failed: vitepress (Node heap out of memory, exit 134).

### 10,000 pages × 50 KB (13/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| jekyll | ruby | 11.8 | 0.8% | 846 | 1,426 |
| zola | rust | 25.5 | 0.2% | 392 | 6,067 |
| metalsmith-handlebars | javascript | 65.5 | 0.0% | 153 | 2,344 |
| metalsmith-nunjucks | javascript | 91.5 | 0.9% | 109 | 2,301 |
| hugo | go | 101.6 | 1.0% | 98 | 7,788 |
| nextjs-export | javascript | 121.9 | 0.1% | 82 | 1,402 |
| jigsaw | php | 194.2 | 0.3% | 51 | 1,153 |
| middleman | ruby | 339.7 | 0.3% | 29 | 853 |
| pelican | python | 689.9 | 0.6% | 14 | 790 |
| nanoc | ruby | 840.5 | 1.8% | 12 | 3,489 |
| mkdocs | python | 1,142.9 | 1.9% | 9 | 2,551 |
| nikola-mako | python | 1,768.8 | 1.9% | 6 | 448 |
| gatsby | javascript | 2,096.8 | 1.8% | 5 | 4,147 |

Failed: astro (Node heap out of memory, exit 134); eleventy (Node heap out of memory, exit 134); hexo (Node heap out of memory, exit 134); vitepress (Node heap out of memory, exit 134).

## GG: 100,000 pages

### 100,000 pages × 5 KB (9/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| zola | rust | 35.2 | — | 2,842 | 7,200 |
| jekyll | ruby | 81.3 | — | 1,230 | 2,271 |
| hugo | go | 102.7 | — | 974 | 6,908 |
| jigsaw | php | 289.3 | — | 346 | 3,656 |
| middleman | ruby | 592.4 | — | 169 | 2,255 |
| pelican | python | 1,074.1 | — | 93 | 1,052 |
| mkdocs | python | 1,097.2 | — | 91 | 2,691 |
| nikola-mako | python | 1,836.9 | — | 54 | 3,828 |
| nanoc | ruby | 3,260.9 | — | 31 | 5,379 |

Failed: astro (Node heap out of memory, exit 134); eleventy (Node heap out of memory, exit 134); gatsby (timeout); hexo (Node heap out of memory, exit 134); metalsmith-handlebars (build error, exit 1); metalsmith-nunjucks (build error, exit 1); nextjs-export (stats parsing bug, fixed in #16); vitepress (Node heap out of memory, exit 134).

### 100,000 pages × 50 KB (1/17 ok)

| Generator | Language | Median (s) | CV | Posts/s | Peak RSS (MB) |
|---|---|---|---|---|---|
| pelican | python | 4,805.4 | — | 21 | 7,534 |

Failed: astro (Node heap out of memory, exit 134); eleventy (Node heap out of memory, exit 134); gatsby (timeout); hexo (Node heap out of memory, exit 134); hugo (8 GB memory limit); jekyll (8 GB memory limit); jigsaw (8 GB memory limit); metalsmith-handlebars (build error, exit 1); metalsmith-nunjucks (build error, exit 1); middleman (8 GB memory limit); mkdocs (8 GB memory limit); nanoc (8 GB memory limit); nextjs-export (8 GB memory limit); nikola-mako (timeout); vitepress (Node heap out of memory, exit 134); zola (8 GB memory limit).
