# 009 Output Quality

- **Date:** 2026-10-10
- **Status:** implemented
- **Repo:** `ssgberk/benchmark-tool` (BT). No change to `ssgberk/ssg-frameworks` (SF).
- **Issue:** #22
- **Related:** BT `008-benchmark-methodology` (suites, `results.json`, environment fingerprint), BT `006-results-summary` (`summary.md`), SF `005-reference-site-design` (what is built, R-14 page set), SF `006-layout-conformance` (post page resolved from the index).

## Context

The toolset measures how long a cold build takes and what it costs: wall time, CPU, peak RSS, input and output bytes, image build time (BT 008). SF 001 and SF 006 only prove that the output is the reference site: same pages, same selectors, same counts. SF 006 leaves out visual comparison, CSS rendering and accessibility audits.

Every generator renders the same reference site, with the same content, templates and stylesheet, so the output is directly comparable. The differences come from the generator itself: hydration and client-side JS, extra requests, minification, extra pages, markup validity and accessibility, and the SEO signals it injects. None of this is measured today.

This spec adds an **untimed quality pass** over the output of one build per generator. It adds no build metric and does not change how builds are timed.

## Requirements

### Running the pass

- **R-1** `--quality` enables the pass. Without `--suite`, it runs in the cell given by `-nf`/`-cs`. With `--suite`, it runs only in the cell `numberOfFiles=50, contentSize=5` (suite P, cell 0), and in every other cell it only logs that the pass was skipped.
- **R-2** The pass runs after the timed runs of a generator succeed (status `ok`). It never runs for `failed`, `timeout`, `oom`, `nonconformant` or `unsupported` results, and it never changes a timing, a status or a ranking.
- **R-3** Before the build container is removed, `DockerHelper` copies `<WorkingDir>/<output_folder>` out of it with `container.get_archive()` into `results/<ts>/quality/<generator>/site/`. `WorkingDir` comes from the container config, and `output_folder` comes from `benchmark_config.json`. That folder holds the output of the last timed build.
- **R-4** The checks run in a BT-owned image built from `quality/Dockerfile`, with pinned versions of Node, Playwright's Chromium build, Lighthouse, axe-core, html-validate and lychee. Chrome for Testing has no Linux arm64 build, but Playwright ships Chromium for both architectures. Its container runs with `network_mode="none"`. The site goes in with `put_archive` and `raw.json` comes out with `get_archive`. Nothing is bind-mounted, because the toolset itself runs in a container and host paths differ.
- **R-5** Inside that container, one static server serves the site on `127.0.0.1` with gzip on and fixed headers. `quality/run.mjs` runs every check against it and writes `quality.json`.
- **R-6** The pinned tool versions (Lighthouse, Chromium, axe-core, html-validate, lychee, Node) and the quality image id are recorded in `results.json` `environment.quality`.

### URLs

- **R-7** Three URLs are audited: the index `/`, one post page and `/404.html`. The post page is the first `a[href]` inside `.post-item`, the same link SF 006 resolves.

### Checks

- **R-8 Lighthouse:** the mobile preset (simulated throttling) and the desktop preset, with 3 runs per URL and preset. Each run records:
  - the scores for performance, accessibility, best-practices and SEO;
  - FCP, LCP, TBT, CLS and Speed Index;
  - total byte weight, JS bytes, CSS bytes, request count and DOM size;
  - the ids of failed audits.

  `quality.json` stores, for each numeric value, the median and range of the 3 runs, and stores the failed audit ids of the median run.
- **R-9 SEO signals:** reported per page, not scored.
  - `<title>` (present, length), `html[lang]`, `meta[name=description]` (present, length), `meta[name=viewport]`, `link[rel=canonical]`.
  - Open Graph `og:title`, `og:description`, `og:type` and `og:url`, and `twitter:card`.
  - JSON-LD: blocks present and whether each one parses.
  - The `meta[name=robots]` value and `link[rel=alternate][hreflang]` count.
  - The `h1` count, whether the heading levels skip, `img` without `alt`, and `a` with no text or accessible name.

  Site-wide: `robots.txt` present, `sitemap.xml` present and valid (and its URL count), RSS or Atom feed present, and favicon present. For a page, `seo.present` counts the per-page signals found, out of a fixed total that `plan.md` lists.
- **R-10 HTML validity:** `html-validate` error and warning counts per page, plus the rule ids.
- **R-11 Accessibility:** axe-core violations per page, counted by impact (critical, serious, moderate, minor), plus the rule ids.
- **R-12 Links:** `lychee --offline` over the whole site. Count the broken internal links, anchors and asset references, and list up to 20 of them.
- **R-13 Weight:**
  - total output bytes, gzip bytes and brotli bytes;
  - bytes per post page;
  - generator-added bytes, which is the total minus the SF 005 reference assets (`assets/ssgberk.css`, `assets/ssgberk.png`). Every generator ships those assets unchanged.
- **R-14 JavaScript:**
  - JS bytes requested per audited page (from Lighthouse) and JS bytes on disk;
  - `worksWithoutJs`, true when the post page's static HTML already contains the post title and the first body paragraph.

  `jsClass` is `none` (0 bytes of JS on every audited page) or `hydrated` (any JS).
- **R-15 Extra output:** files outside the SF 005 page set (index, post pages, `404.html`, reference assets), counted and sized and grouped by extension.

### Results

- **R-16** `quality.json` has one section per check (`lighthouse`, `seo`, `html`, `a11y`, `links`, `weight`, `js`, `extra`). Each section carries `status` (`ok` or `error`) and, on error, `error` with the message. A failing check is a result, not an error: it never fails the generator, the cell or the run.
- **R-17** `results.json` gets `quality.<generator>`: the parsed `quality.json`, or `{"status": "error", "error": ...}` when the pass could not run.
- **R-18** `summary.md` gets a "Qualidade" section with one row per generator. The columns are:
  - the 4 mobile Lighthouse scores and mobile LCP;
  - the post page's JS bytes, `jsClass` and gzip bytes;
  - the HTML error, axe violation and broken link counts;
  - SEO signals present, as `n/total`.

  Rows are sorted by name, with no combined score and no ranking. `quality-summary.csv` holds the same columns plus every numeric field. The rounds page reads that file; the page itself is not in this repository.
- **R-19** The section notes that the SF 005 templates carry no meta description and no viewport, so every generator loses the same SEO points. That constant isn't a difference between generators.

## Goals and success criteria

1. **One command audits the output.** *Measured by:* `./ssgberk --test hugo -nf 50 -cs 5 --quality` writes `results/<ts>/quality/hugo/quality.json` with all 8 sections and `status: ok`. A unit test asserts that `rawData`, `succeeded`, `failed` and the rankings in `summary.md` are identical with and without a `quality` section for the same parsed build output.
2. **The pass is isolated.** *Measured by:* a unit test asserts that the quality container runs with `network_mode="none"` and no volumes or mounts. Another asserts that a raised error in the pass leaves the build result unchanged and records `quality.<fw>.status = "error"`.
3. **Checks are pinned and recorded.** *Measured by:* `environment.quality` lists every tool version from R-6, and `quality/Dockerfile` names an exact version for each one.
4. **The matrix runs in CI.** *Measured by:* a BT CI job runs the pass on hugo for `ubuntu-24.04` and `ubuntu-24.04-arm`, and checks that every section is present and every score is between 0 and 1. A `workflow_dispatch` input runs it on every generator, one job each, and the job succeeds even when a check reports failures.

## Testing

- **pytest (no Docker):**
  - SEO signal extraction from the SF 005 reference page and from variants (with description, with OG tags, with a broken JSON-LD block, a skipped heading level, `img` without `alt`);
  - the Lighthouse median and range reduction;
  - the axe and html-validate count reduction;
  - extra output classification;
  - weight arithmetic;
  - the `quality.json` to `results.json` and `summary.md` merge;
  - the R-1 skip rules.
- **Inside the quality image:** `quality/run.mjs` runs against a 3-page fixture site (index, one post, 404) and its `quality.json` matches a checked-in expected shape (keys and types, not Lighthouse values).

## Out of scope

- New build metrics: install time, image size breakdown, incremental builds, startup cost.
- Determinism (building twice and comparing the trees), because it needs a second build.
- A combined quality score or ranking.
- Changes to the SF 005 reference site, the SF 006 conformance rules or any generator.
- Field data, RUM and real-user Core Web Vitals.
- Tuning generators to score better: the pass audits the reference configuration as built.
