# 009 Output Quality: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. The steps are in `tasks.md` and use checkbox (`- [ ]`) syntax for tracking.

**Goal:** an untimed quality pass that audits the output of one build per generator (Lighthouse, SEO signals, HTML validity, accessibility, links, weight, JS, extra output) and writes `quality.json`, `results.json` `quality`, a "Qualidade" section in `summary.md` and `quality-summary.csv`.

**Architecture:**
1. **Export.** `DockerHelper.benchmark` copies the build output out of the generator container before removing it.
2. **Collection.** A pinned BT image (`quality/`) runs a Node collector (`quality/run.mjs`) with no network. The collector serves the site, runs Lighthouse, axe-core, html-validate and lychee, and measures file sizes. It writes raw data only (`raw.json`).
3. **Reduction.** Pure Python in `toolset/quality/` reduces `raw.json` into `quality.json` and computes the SEO signals, the pages, the JS check and the extra output from the exported files. Most of the logic is therefore testable with pytest and no Docker.

**Tech stack:**
- **Toolset:** Python 3.12 stdlib (`html.parser`, `tarfile`, `xml.etree`, `statistics`, `fnmatch`) and docker-py 7.1.0, as in the existing toolset.
- **Collector:** Node 24 with the `lighthouse`, `chrome-launcher`, `playwright` (Chromium only), `axe-core` and `html-validate` npm packages, plus the `lychee` binary.

**Spec:** `docs/specs/009-output-quality/spec.md`. Read it before any task; requirement ids (R-n) below refer to it.

## Global Constraints

- The pass never changes a timing, a status, `succeeded`/`failed` or a ranking (R-2, goal 1).
- The quality container runs with `network_mode="none"` and has no volumes or mounts. The site goes in with `put_archive`; `raw.json` comes out with `get_archive` (R-4, goal 2).
- Every tool version is pinned exactly:
  - npm: exact versions in `quality/package.json` and a committed `quality/package-lock.json`;
  - Node, lychee: `ARG` with a full version in `quality/Dockerfile`;
  - Chromium: whatever the pinned `playwright` version installs (R-4, R-6).
- With `--suite`, the pass runs only in the cell `numberOfFiles=50, contentSize=5` (R-1).
- A failing check is a section with `status: "error"` and `error: "<message>"`, never an exception out of the pass (R-16).
- Three audited URLs: `/`, the first `a[href]` inside `.post-item` on the index, and `/404.html` (R-7).
- Lighthouse: mobile and desktop presets, 3 runs per URL and preset, median and range per value, failed audit ids of the median run (R-8).
- No combined score and no ranking in any output (R-18).
- Toolset code is stdlib plus `docker`, and passes `ruff check toolset tests`. Tests run with `pytest -q` and need no Docker.
- Commits: author and committer `Matheus Breguêz <matbrgz@gmail.com>`, GPG-signed (key `B6FA8458D5176E83`), trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`. Never use `--no-gpg-sign` or `--author`.

## Review Focus

1. **The post link is relative, has a query or fragment, or ends without `/`.** Examples: `post/a/`, `./post/a/index.html`, `/post/a?x=1#t`, `/post/a`. `resolve_pages` must still find the file on disk. Pinned in Task 1 (`test_resolve_pages_variants`).
2. **A generator writes non-UTF-8 bytes or a malformed HTML page.** SEO extraction and `works_without_js` must not raise; they read with `errors="replace"` and `html.parser` tolerates bad markup. Pinned in Task 2 (`test_page_signals_malformed_html`).
3. **The collector fails for one page or one check.** For example, Lighthouse times out on the 404 page, or lychee is missing. The other pages and sections must still be reported, and only the affected entry is an `error`. Pinned in Task 3 (`test_build_quality_partial_errors`).
4. **The exported archive is missing,** because the export failed or the noise re-run timed out. The pass records `quality.<fw>.status = "error"` and the build result is unchanged. Pinned in Task 6 (`test_quality_pass_missing_archive_keeps_result`).
5. **`--parse` on a run that had a quality pass.** `quality` must survive the re-parse, because raw.txt cannot rebuild it. Pinned in Task 6 (`test_reparse_keeps_quality`).

## File structure

| File | Responsibility | Task |
|---|---|---|
| `toolset/quality/__init__.py` | package marker | 1 |
| `toolset/quality/site.py` | generator config (`output_folder`, `output_glob`), archive extraction, page resolution (R-7), URL to file, extra output (R-15), `works_without_js` (R-14) | 1 |
| `toolset/quality/seo.py` | per-page and site-wide SEO signals (R-9) | 2 |
| `toolset/quality/reduce.py` | `raw.json` to `quality.json`: Lighthouse, axe, html-validate, lychee, weight, JS reductions and section assembly (R-8, R-10..R-14, R-16) | 3 |
| `quality/Dockerfile`, `quality/package.json`, `quality/package-lock.json`, `quality/run.mjs` | the pinned collector image (R-4, R-5) | 4 |
| `quality/test/fixture/**`, `quality/test/pages.json`, `quality/test/expected-shape.json`, `quality/test/check-shape.mjs` | collector test inside the image | 4 |
| `toolset/utils/docker_helper.py` | output export in `benchmark`, `build_quality_image`, `run_quality` | 5 |
| `toolset/quality/runner.py` | `eligible` (R-1), `archive_path`, `run_pass` (R-3, R-16) | 6 |
| `toolset/run-tests.py`, `toolset/utils/benchmark_config.py` | `--quality` flag | 6 |
| `toolset/benchmark/benchmarker.py` | export arguments and the pass hook (R-2) | 6 |
| `toolset/utils/results.py` | `add_quality`, `quality` and `environment.quality` in `results.json`, kept by `--parse` (R-6, R-17) | 6 |
| `toolset/utils/summary.py` | `quality_rows`, `quality_csv`, `quality_markdown`; the section in `to_markdown` (R-18, R-19) | 7 |
| `.github/workflows/ci.yml`, `.github/workflows/benchmark-round.yml`, `README.md` | CI jobs, round input, docs (goal 4) | 8 |
| `tests/test_quality_site.py`, `tests/test_quality_seo.py`, `tests/test_quality_reduce.py`, `tests/test_quality_docker.py`, `tests/test_quality_runner.py`, `tests/test_quality_summary.py`, `tests/fixtures/quality/**` | tests | 1–7 |

## Contracts

### Collector CLI (`quality/run.mjs`)

```
node /quality/run.mjs --site <dir> --pages '<json>' --out <dir>
```

`--pages` is the object returned by `site.resolve_pages`, for example:

```json
{"index": {"url": "/", "file": "index.html"},
 "post": {"url": "/post/hello/", "file": "post/hello/index.html"},
 "404": {"url": "/404.html", "file": "404.html"}}
```

The collector writes `<out>/raw.json` and exits 0, even when checks fail. It exits non-zero only if it cannot write `raw.json`.

### `raw.json` (collector output, input of `reduce.build_quality`)

Any top-level section may instead be `{"error": "<message>"}`, and any page entry may be `{"error": "<message>"}`.

```json
{
  "tools": {"node": "v24.x", "lighthouse": "x.y.z", "chromium": "x.y", "axeCore": "x.y.z",
            "htmlValidate": "x.y.z", "lychee": "x.y.z", "playwright": "x.y.z"},
  "pages": {"index": {"url": "/", "file": "index.html"}, "post": {...}, "404": {...}},
  "lighthouse": {
    "mobile":  {"index": [RUN, RUN, RUN], "post": [...], "404": [...]},
    "desktop": {"index": [...], "post": [...], "404": [...]}
  },
  "axe": {"index": {"violations": [{"id": "color-contrast", "impact": "serious", "nodes": 3}]}, "post": {...}, "404": {...}},
  "rendered": {"post": {"title": "Post title", "firstParagraph": "First paragraph text"}},
  "html": {"index": {"messages": [{"ruleId": "void-style", "severity": 2}]}, "post": {...}, "404": {...}},
  "links": {"report": <lychee --format json output>},
  "files": [{"path": "index.html", "bytes": 1234, "gzip": 600, "br": 500}]
}
```

`RUN` is either `{"error": "<message>"}` or:

```json
{"scores": {"performance": 0.98, "accessibility": 1, "best-practices": 1, "seo": 0.82},
 "metrics": {"fcp": 812.3, "lcp": 812.3, "tbt": 0, "cls": 0, "si": 812.3},
 "resources": {"totalBytes": 5321, "jsBytes": 0, "cssBytes": 1210, "requests": 3, "domSize": 54},
 "failedAudits": ["meta-description"]}
```

Metric units are Lighthouse's `numericValue`: milliseconds for FCP, LCP, TBT and SI, unitless for CLS.

### `quality.json` (R-16)

```json
{
  "status": "ok",
  "pages": {"index": "/", "post": "/post/hello/", "404": "/404.html"},
  "postSource": "index",
  "tools": {...copied from raw.json...},
  "lighthouse": {"status": "ok",
    "mobile": {"post": {"status": "ok", "runs": 3,
      "scores": {"performance": {"median": 0.98, "min": 0.97, "max": 0.99}, ...},
      "metrics": {"lcp": {"median": 812.3, "min": ..., "max": ...}, ...},
      "resources": {"jsBytes": {"median": 0, ...}, ...},
      "failedAudits": ["meta-description"]}, "index": {...}, "404": {...}},
    "desktop": {...}},
  "seo": {"status": "ok", "total": 12,
    "pages": {"index": {...signals...}, "post": {...}, "404": {...}},
    "present": {"index": 2, "post": 2, "404": 2},
    "site": {"robotsTxt": false, "sitemap": {"present": false, "valid": null, "urls": null},
             "feed": false, "favicon": false}},
  "html": {"status": "ok", "pages": {"index": {"errors": 0, "warnings": 1, "rules": ["..."]}, ...}},
  "a11y": {"status": "ok", "pages": {"index": {"violations": {"critical": 0, "serious": 1, "moderate": 0, "minor": 0},
                                                "total": 1, "rules": ["color-contrast"]}, ...}},
  "links": {"status": "ok", "broken": 0, "byKind": {"link": 0, "anchor": 0, "asset": 0}, "items": []},
  "weight": {"status": "ok", "bytes": 0, "gzipBytes": 0, "brotliBytes": 0, "bytesPerPost": 0,
             "generatorAddedBytes": 0},
  "js": {"status": "ok", "pages": {"index": 0, "post": 0, "404": 0}, "diskBytes": 0,
         "jsClass": "none", "worksWithoutJs": true},
  "extra": {"status": "ok", "files": 0, "bytes": 0, "byExtension": {}}
}
```

When the whole pass fails, `quality.json` is `{"status": "error", "error": "<Type>: <message>"}`.

### Python interfaces

- **`toolset/quality/site.py`:**
  - `REFERENCE_ASSETS = ('assets/ssgberk.css', 'assets/ssgberk.png')`
  - `generator_config(test_directory) -> (output_folder: str, output_glob: str)`
  - `extract(tar_path, dest) -> str`: extracts the archive and strips its top directory; returns `dest`.
  - `url_to_file(site_dir, url) -> str | None`
  - `resolve_pages(site_dir) -> dict` (shape above); raises `ValueError`.
  - `list_files(site_dir) -> list[str]`: sorted POSIX relative paths.
  - `extra_output(site_dir, output_glob) -> {"files", "bytes", "byExtension"}`
  - `works_without_js(site_dir, post_file, rendered) -> bool | None`
- **`toolset/quality/seo.py`:**
  - `PAGE_SIGNALS` (tuple of 12 keys)
  - `page_signals(html: str) -> dict`
  - `site_signals(site_dir, page_signals_list) -> dict`
  - `seo_section(site_dir, pages) -> {"total", "pages", "present", "site"}`
- **`toolset/quality/reduce.py`:**
  - `SECTIONS`, `spread(values)`
  - `reduce_lighthouse(raw_lh)`, `reduce_axe(raw_axe)`, `reduce_html(raw_html)`, `reduce_links(raw_links)`
  - `weight(files, output_glob)`, `js_section(lighthouse, files, works)`
  - `build_quality(raw, site_dir, pages, output_glob) -> dict`
- **`toolset/quality/runner.py`:**
  - `QUALITY_CELL = (50, 5.0)`
  - `eligible(config) -> bool`
  - `skipped(config) -> bool`: `--quality` was given but this cell is not eligible.
  - `archive_path(results_dir, name) -> str`
  - `run_pass(docker_helper, test, results_dir) -> dict`, which never raises.
- **`toolset/utils/docker_helper.py`:**
  - `QUALITY_IMAGE = 'ssgberk/quality'`, `QUALITY_TIMEOUT_SECONDS = 1800`
  - `DockerHelper.benchmark(..., export=None)`, where `export` is `(output_folder, dest_tar_path)`
  - `DockerHelper.build_quality_image() -> str` (image id)
  - `DockerHelper.run_quality(tar_path, site_name, pages, timeout_seconds=QUALITY_TIMEOUT_SECONDS) -> dict` (raw.json)
- **`toolset/utils/results.py`:** `Results.add_quality(name, quality, image_id=None)`
- **`toolset/utils/summary.py`:**
  - `QUALITY_COLUMNS`
  - `quality_rows(results) -> list[dict]`
  - `quality_csv(rows) -> str`
  - `quality_markdown(rows) -> list[str]`

## Decisions

1. **The collector writes raw data, and Python reduces it.** Medians, counts, the SEO signals and the page set live in Python so they are covered by pytest without Docker or Chrome (spec "Testing"). The collector only does what needs a browser or a binary.
2. **One Chromium, two drivers.** Lighthouse drives Playwright's Chromium through `chrome-launcher` (`chromePath = chromium.executablePath()`). axe-core and the rendered-text check use Playwright on the same binary. Chrome runs with `--headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage`, because the container runs as root and `/dev/shm` is small.
3. **The static server is a few lines of Node `http`.** It has gzip, fixed headers and directory index, and it serves `404.html` with status 404, so no server package version can change the results.
4. **The summary uses the post page.** The 4 scores and LCP in the `summary.md` row come from the mobile preset on the post page, the page type that scales with the site. `quality.json` keeps every page and both presets.
5. **The image builds outside the time logger.** `build_quality_image` streams its own `APIClient.build`, so the generator's build-time log lines and `imageBuild` are not touched. It builds once per process, the first time a pass runs.
6. **No new dependency in the toolset image.** brotli is computed by the collector (Node `zlib`), not by Python.
7. **The export is skipped when the build did not end `ok` with exit code 0.** For a noisy re-run, the export of the re-run overwrites the first one, so the audited output is always the last build.
8. **The sitemap is parsed with `xml.etree.ElementTree`, not `defusedxml`.** The toolset stays stdlib plus `docker`. `sitemap.xml` comes from the generator under test, not from the network. ElementTree never fetches external entities, and the expat bundled with Python 3.12 limits entity expansion (billion laughs). A parse error is recorded as `valid: false`.
9. **What happens to the exported files.** The extracted site stays in `results/<ts>/quality/<fw>/site/` for inspection. `site.tar` is deleted after the pass.
