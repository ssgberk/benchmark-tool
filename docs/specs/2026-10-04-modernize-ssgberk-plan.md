# SSGBerk 2026 Modernization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `./ssgberk` run on a current machine (Docker 29, Linux amd64 / macOS arm64) and record real build times for 17 static site generators in `results.json`.

**Architecture:** Minimal Python 2→3 port of the TechEmpower-derived toolset in `ssgberk/benchmark-tool`, plus one functional fix: a marker-delimited hyperfine JSON contract between each generator's `build.sh` and `Results.parse_test`. Generators live in `ssgberk/ssg-frameworks` (mounted as submodule `frameworks/`), each with an Ubuntu 24.04 dockerfile, an identical canonical `build.sh`, and a minimal site.

**Tech Stack:** Python 3.12 (toolset image) / 3.14 (host dev), docker-py 7.1.0, pytest, ruff, dool 1.3.8, hyperfine 1.20.0, Ubuntu 24.04, Node 24.21.0, Ruby 3.2 (apt), PHP 8.4, GitHub Actions.

**Spec:** `docs/specs/2026-10-04-modernize-ssgberk-design.md` (same directory). Read it before starting any task.

## Workspace layout (already created / created in Task 0)

```
/Users/jobs/Dev/ssgberk/
  benchmark-tool/                         # main checkout, branch master — DO NOT EDIT
  ssg-frameworks/                         # main checkout, branch master — DO NOT EDIT
  StaticSiteGeneratorBenchmark/           # monorepo, read-only reference source
  .worktrees/benchmark-tool-modernize/    # benchmark-tool, branch chore/modernize-2026  ← BT
  .worktrees/benchmark-tool-modernize/frameworks/
                                          # ssg-frameworks worktree, branch chore/modernize-2026 ← SF
```

In this plan **BT** = `/Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize` and **SF** = `BT/frameworks`. SF lives inside BT on purpose: `./ssgberk` mounts BT into the toolset container and reads generators from `BT/frameworks`, so local end-to-end runs exercise the in-progress generators without touching the submodule pointer.

## Global Constraints

- Git author/committer `Matheus Breguêz <matbrgz@gmail.com>`; every commit GPG-signed (repo config already has `commit.gpgsign=true`, key `B6FA8458D5176E83`). Never use `--no-gpg-sign` or `--author`.
- Every commit message ends with the trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Never commit to `master`. Never push, open PRs, or close dependabot branches unless the human explicitly asks.
- Toolset image tag: `ssgberk/toolset`. Generator image tag: `ssgberk/test.<name>`. No `matheusrv` strings may remain in `toolset/`, `ssgberk`, or `Dockerfile`.
- Generator base image `ubuntu:24.04`; architecture detected **inside `RUN`** with `ARCH="$(dpkg --print-architecture)"` (`amd64`|`arm64`). Never rely on `TARGETARCH` (empty under the legacy builder docker-py uses — verified on Docker 29).
- Pinned versions: hyperfine `1.20.0`, dool `v1.3.8`, docker-py `7.1.0`, Node `24.21.0`, hugo `0.167.0`, zola `0.23.6`, jekyll `4.4.1`, nanoc `4.14.8`, middleman `4.6.3`, nikola `8.3.3`, pelican `4.12.0`, mkdocs `1.6.1`, jigsaw `v1.8.8`, metalsmith `2.7.0`, gatsby `5.16.1`, astro `7.3.5`, @11ty/eleventy `3.1.6`, hexo `8.1.2`, next `16.3.8`, vitepress `1.6.4`.
- `-cs` values and meaning (KB per post): `0.500`=1 paragraph, `500`=1000, `1000`=2000, `5000`=10000, `10000`=20000, `100000`=200000 paragraphs. Default `0.500`.
- Result markers printed by `build.sh`, consumed by `Results.parse_test`: `SSGBERK_RESULT_BEGIN`, `SSGBERK_RESULT_END`, `SSGBERK_VERIFY_FAIL`, `STARTTIME <epoch>`, `ENDTIME <epoch>`.
- Generated post filenames are `YYYY-MM-DD-NNN.<ext>` (NNN zero-padded by `seq -w`). `build.sh` only ever deletes entries in the content folder matching `[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*`, so section index files (e.g. `_index.md`, `posts.json`) survive.
- Every generator's `build.sh` is byte-identical to `SF/Go/hugo/build.sh`.
- A generator's directory name equals its `benchmark_config.json` `framework` value and its test name (CI derives the test name from the directory basename).
- No themes, plugins, minification or speed tweaks in generator sites: base layout + post template + index listing posts.

## Generator Dockerfile skeleton (used by Tasks 7–22)

Every `<name>.dockerfile` has exactly this shape; tasks fill in the RUNTIME and GENERATOR blocks and `<name>`:

```dockerfile
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG HYPERFINE_VERSION=1.20.0

RUN apt-get -yqq update \
 && apt-get -yqq install --no-install-recommends \
      build-essential ca-certificates curl git jq moreutils tree wget xz-utils \
 && rm -rf /var/lib/apt/lists/*

RUN ARCH="$(dpkg --print-architecture)" \
 && curl -fsSL -o /tmp/hyperfine.deb \
      "https://github.com/sharkdp/hyperfine/releases/download/v${HYPERFINE_VERSION}/hyperfine_${HYPERFINE_VERSION}_${ARCH}.deb" \
 && dpkg -i /tmp/hyperfine.deb && rm /tmp/hyperfine.deb

# ---- RUNTIME block (per task) ----

WORKDIR /opt/<name>/src

# ---- GENERATOR block (per task): copy manifests, install deps ----

COPY src/ /opt/<name>/src/
COPY build.sh benchmark_config.json /opt/<name>/src/
```

Node RUNTIME block (JS generators):

```dockerfile
ARG NODE_VERSION=24.21.0
RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in amd64) NARCH=x64 ;; arm64) NARCH=arm64 ;; *) echo "unsupported $ARCH"; exit 1 ;; esac \
 && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1 \
 && node --version && npm --version
```

Ruby RUNTIME block:

```dockerfile
RUN apt-get -yqq update \
 && apt-get -yqq install --no-install-recommends ruby ruby-dev zlib1g-dev libffi-dev libyaml-dev \
 && rm -rf /var/lib/apt/lists/* \
 && gem install bundler --no-document
```

Python RUNTIME block:

```dockerfile
RUN apt-get -yqq update \
 && apt-get -yqq install --no-install-recommends python3 python3-venv python3-dev \
 && rm -rf /var/lib/apt/lists/* \
 && python3 -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH
```

## Generator smoke procedure (used by Tasks 7–22)

From BT, after the toolset tasks are done:

```bash
cd /Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize
./ssgberk --test <name> -nf 10 -cs 0.500 -mr 1
R=$(ls -td results/*/ | head -1)
jq -e '.succeeded.datarate | index("<name>")' "$R/results.json"
jq -e '.rawData.datarate["<name>"][0].mean > 0' "$R/results.json"
grep -c SSGBERK_VERIFY_FAIL "$R/<name>/datarate/raw.txt"   # must print 0
```

Expected: both `jq -e` exit 0; grep prints `0`. Also confirm the glob is exact: run the generator image by hand with `-nf 10` and check the verify line in `raw.txt` reads `SSGBERK_VERIFY_OK expected=10 got=10` (got must equal expected, not exceed it — if it exceeds, the glob matches non-post pages; tighten it).

Commit per generator inside SF:

```bash
cd /Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize/frameworks
git add -A <Lang>/<name>
git commit -m "feat(<name>): <update to|add> <version> on ubuntu 24.04

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

If a generator cannot be made to pass after a genuine attempt (native gem fails to build, upstream bug): inside SF run `git mv <Lang>/<name> _wip/<Lang>/<name>`, add `_wip/<Lang>/<name>/WIP.md` with the exact error output, commit, and report the task as DONE_WITH_CONCERNS. `Metadata.gather_tests` globs `frameworks/*/*/benchmark_config.json`, so `_wip/<Lang>/<name>` (three levels) is not picked up.

## Review Focus

1. **Chunked docker log stream corrupting the JSON** — `container.logs(stream=True)` yields arbitrary byte chunks; if `raw.txt` is written through `log()` (which appends a newline per chunk) a number like `12.34` can be split into `12.` / `34` and parsing silently fails, sending every generator to `failed`. Pinned by `test_benchmark_writes_raw_chunks_verbatim` in Task 3.
2. **Incremental builds masking timings** — a generator reusing its previous output (jekyll `--incremental`, gatsby cache, astro cache) reports near-zero times after run 1. Expect `build.sh` to delete the output folder and known caches before every hyperfine run via `--prepare`. Pinned by the `prepare` assertion in Task 6's `test_build_sh.bats`-style shell test (`tests/build_sh/test_build_sh.sh`) and per-generator `cache_folders`.
3. **Glob matching more than the posts** — `output_glob` that also matches index/tag pages makes a broken post template look "OK". Expect verification to require `got == expected` for an empty site. Pinned by `test_verify_counts_exact` in Task 6.
4. **Sample posts shipped in `src/`** — old sample content (e.g. jekyll `_posts/2014-*.md`) inflates the workload and the count. Expect `build.sh` to remove date-named entries before generating. Pinned by `test_reset_removes_only_dated_entries` in Task 6.
5. **Unknown / legacy `-cs` value** — `[500]` from old scripts or `0.500` must keep their meaning; an unknown value must fail loudly, not silently fall back to one paragraph. Pinned by `test_content_size_unknown_fails` in Task 6 and `test_cs_rejects_unknown` in Task 2.

---

## Phase A — `benchmark-tool` (all paths relative to BT)

### Task 0: Workspace and dev tooling

**Files:**
- Create: `requirements-dev.txt`, `pyproject.toml`, `tests/__init__.py`, `tests/conftest.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `.venv` with deps; `tests/conftest.py::fake_benchmarker(tmp_path)` fixture returning an object with `.config` (attributes listed below) and `.results`-free; used by Tasks 1–3.

- [ ] **Step 1: Create the SF worktree inside BT**

```bash
cd /Users/jobs/Dev/ssgberk/ssg-frameworks
git worktree add -b chore/modernize-2026 /Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize/frameworks master
cd /Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize
ls frameworks   # Expected: Go JavaScript LICENSE PHP Python Ruby
```

If `git worktree add` complains the directory exists, it is the empty submodule dir: `rmdir frameworks` then rerun.

- [ ] **Step 2: Write `requirements-dev.txt`**

```
colorama==0.4.6
docker==7.1.0
psutil==7.0.0
requests==2.32.3
pytest==8.3.5
ruff==0.11.8
```

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
target-version = "py312"
extend-exclude = ["frameworks"]

[tool.ruff.lint]
select = ["E9", "F63", "F7", "F82", "UP003", "UP004", "UP008", "UP025"]
```

- [ ] **Step 4: Append to `.gitignore`**

```
.venv/
.pytest_cache/
.ruff_cache/
```

- [ ] **Step 5: Create venv and the shared fixture**

```bash
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
touch tests/__init__.py
```

`tests/conftest.py`:

```python
import types

import pytest


@pytest.fixture
def fake_config(tmp_path):
    cfg = types.SimpleNamespace(
        fw_root=str(tmp_path),
        lang_root=str(tmp_path / "frameworks"),
        results_root=str(tmp_path / "results"),
        timestamp="20261004000000",
        results_name="test-run",
        results_environment="pytest",
        results_upload_uri=None,
        number_of_files="10",
        content_size="0.500",
        min_runs="1",
        verbose_build=False,
        duration=15,
        test=None,
        test_dir=None,
        test_lang=None,
        exclude=None,
        types={},
    )
    (tmp_path / "frameworks").mkdir()
    return cfg


@pytest.fixture
def fake_benchmarker(fake_config):
    return types.SimpleNamespace(config=fake_config, tests=[])
```

- [ ] **Step 6: Commit**

```bash
git add requirements-dev.txt pyproject.toml tests .gitignore
git commit -m "chore: add python 3 dev tooling (pytest, ruff)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

(The `frameworks/` worktree shows as modified submodule content in `git status`; never `git add frameworks` until Task 23.)

### Task 1: Python 3 port of the toolset

**Files:**
- Modify: `toolset/benchmark/test_types/__init__.py`, `toolset/utils/metadata.py`, `toolset/utils/scaffolding.py`, `toolset/utils/output_helper.py`, `toolset/utils/docker_helper.py`, `toolset/utils/results.py` (only `__parse_stats` `next()` calls and deletion of unused `__calculate_average_stats`), any other file `compileall`/ruff flags
- Test: `tests/test_imports.py`, `tests/test_metadata.py`

**Interfaces:**
- Consumes: `fake_benchmarker` fixture (Task 0).
- Produces: every `toolset.*` module importable under Python 3; `Metadata.parse_config(config: dict, directory: str) -> list[FrameworkTest]` unchanged signature; `Metadata.list_test_metadata()` writes a JSON **list**.

- [ ] **Step 1: Write failing tests**

`tests/test_imports.py`:

```python
import importlib

import pytest

MODULES = [
    "toolset.benchmark.benchmarker",
    "toolset.benchmark.framework_test",
    "toolset.benchmark.test_types",
    "toolset.utils.audit",
    "toolset.utils.benchmark_config",
    "toolset.utils.cleaner",
    "toolset.utils.docker_helper",
    "toolset.utils.metadata",
    "toolset.utils.output_helper",
    "toolset.utils.results",
    "toolset.utils.scaffolding",
    "toolset.utils.time_logger",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(name)
```

`tests/test_metadata.py`:

```python
import json
import os

from toolset.benchmark.test_types import DatarateTestType
from toolset.utils.metadata import Metadata

CONFIG = {
    "framework": "hugo",
    "tests": [{"default": {
        "approach": "Realistic", "classification": "Micro", "framework": "hugo",
        "language": "Go", "display_name": "hugo", "notes": "", "versus": "go",
    }}],
}


def test_parse_config_builds_default_test(fake_benchmarker):
    fake_benchmarker.config.types = {"datarate": DatarateTestType(fake_benchmarker.config)}
    tests = Metadata(fake_benchmarker).parse_config(CONFIG, "/x/frameworks/Go/hugo")
    assert [t.name for t in tests] == ["hugo"]
    assert list(tests[0].runTests) == ["datarate"]


def test_list_test_metadata_writes_json_list(fake_benchmarker, tmp_path):
    fake_benchmarker.config.types = {"datarate": DatarateTestType(fake_benchmarker.config)}
    d = tmp_path / "frameworks" / "Go" / "hugo"
    d.mkdir(parents=True)
    (d / "benchmark_config.json").write_text(json.dumps(CONFIG))
    fake_benchmarker.results = type("R", (), {"directory": str(tmp_path)})()
    Metadata(fake_benchmarker).list_test_metadata()
    data = json.loads((tmp_path / "test_metadata.json").read_text())
    assert isinstance(data, list) and data[0]["name"] == "hugo"
```

- [ ] **Step 2: Run, expect failures**

Run: `.venv/bin/pytest -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'framework_test_type'` and `AttributeError: 'dict' object has no attribute 'iteritems'`.

- [ ] **Step 3: Apply the port**

1. `toolset/benchmark/test_types/__init__.py`:
   ```python
   from .framework_test_type import *  # noqa: F403
   from .datarate_type import DatarateTestType  # noqa: F401
   ```
2. `toolset/utils/metadata.py`: `test.iteritems()` → `test.items()` (2×); `self.benchmarker.config.types.iteritems()` → `.items()`; in `gather_language_tests` use `tests = list(map(...))` and `return list(filter(...))`; in `list_test_metadata` replace `json.dumps(map(lambda test: {...}, all_tests))` with `json.dumps([{...} for test in all_tests])`, keeping exactly the same keys.
3. `toolset/utils/scaffolding.py`: every `raw_input(` → `input(`.
4. `toolset/utils/output_helper.py`: `if line.strip() is not '':` → `if line.strip() != '':`.
5. `toolset/utils/docker_helper.py` `__build`: call `client.build(..., decode=True)` and replace the token loop head with:
   ```python
   for token in output:
       if 'stream' in token:
           buffer += token['stream']
       elif 'errorDetail' in token:
           raise Exception(token['errorDetail']['message'])
   ```
   (keep the existing `while "\n" in buffer` block and timeout check unchanged inside the loop).
   In `run().watch_container`: `log(line.decode('utf-8', 'replace'), prefix=log_prefix, file=run_log)`.
6. `toolset/utils/results.py`: delete the unused `__calculate_average_stats` method (it is never called and indexes `dict.items()`). Leave `__parse_stats` for Task 3.
7. Run `.venv/bin/python -m compileall -q toolset` and `.venv/bin/ruff check toolset tests`; fix every reported Python-2-ism the same mechanical way (no behavior changes).

- [ ] **Step 4: Run tests**

Run: `.venv/bin/pytest -q && .venv/bin/python -m compileall -q toolset && .venv/bin/ruff check toolset tests`
Expected: all pass, no output from compileall, ruff `All checks passed!`.

- [ ] **Step 5: Commit**

```bash
git add toolset tests
git commit -m "refactor(toolset): port to python 3

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

### Task 2: CLI fixes (`-cs`, `-v`, help texts)

**Files:**
- Modify: `toolset/run-tests.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Produces: `build_parser() -> argparse.ArgumentParser` in `toolset/run-tests.py`; `main()` calls `build_parser().parse_args()`. `args.content_size` is a single `str` from `['0.500','500','1000','5000','10000','100000']`; `args.verbose` is `bool`.

- [ ] **Step 1: Write failing tests** — `tests/test_cli.py`:

```python
import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "run_tests", pathlib.Path(__file__).parent.parent / "toolset" / "run-tests.py")
run_tests = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_tests)


def parse(*argv):
    return run_tests.build_parser().parse_args(list(argv))


def test_cs_default_is_half_kb():
    assert parse().content_size == "0.500"


def test_cs_accepts_100000_as_single_value():
    assert parse("-cs", "100000").content_size == "100000"


def test_cs_rejects_unknown():
    with pytest.raises(SystemExit):
        parse("-cs", "7")


def test_verbose_is_flag():
    assert parse("-v").verbose is True
    assert parse().verbose is False


def test_help_texts_are_specific():
    helps = {a.dest: a.help for a in run_tests.build_parser()._actions}
    assert "number of" in helps["number_of_files"].lower()
    assert "kb" in helps["content_size"].lower()
    assert "runs" in helps["min_runs"].lower()
```

- [ ] **Step 2: Run** — `.venv/bin/pytest tests/test_cli.py -q` → FAIL `AttributeError: module 'run_tests' has no attribute 'build_parser'`.

- [ ] **Step 3: Implement**

Move everything from `parser = argparse.ArgumentParser(` through the last `parser.add_argument(...)` in `main()` into `def build_parser():` (returning `parser`), and in `main()` replace the parser construction and `args = parser.parse_args()` with `args = build_parser().parse_args()`. Change these arguments:

```python
    parser.add_argument(
        '-v', '--verbose', action='store_true', default=False,
        help='Run the generator build command in verbose mode')
    parser.add_argument(
        '-nf', '--number-of-files', default='10',
        help='Number of markdown posts generated for each build')
    parser.add_argument(
        '-cs', '--content-size',
        choices=['0.500', '500', '1000', '5000', '10000', '100000'],
        default='0.500',
        help='Size of each post in KB (0.500 = one paragraph)')
    parser.add_argument(
        '-mr', '--min-runs', default='3',
        help='Number of timed hyperfine runs per build')
```

Also update the `--type` default to `['all']` (list, so `'all' in args.type` stays correct) and the parser `description` to `"Run the Static Site Generator Benchmarks (SSGBerk) suite."`.

- [ ] **Step 4: Run** — `.venv/bin/pytest -q` → all PASS.

- [ ] **Step 5: Commit** — `git add toolset/run-tests.py tests/test_cli.py && git commit -m "fix(cli): single-value content size, boolean verbose, accurate help" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

### Task 3: Results contract (hyperfine JSON, raw output, dool stats)

**Files:**
- Modify: `toolset/utils/results.py` (`parse_test`, `__parse_stats`, new module-level `parse_build_output`), `toolset/utils/docker_helper.py` (`benchmark`), `toolset/benchmark/benchmarker.py` (`__begin_logging`: `dstat` → `dool`)
- Create: `tests/fixtures/raw_ok.txt`, `tests/fixtures/dool.csv`
- Test: `tests/test_results.py`, `tests/test_docker_helper.py`

**Interfaces:**
- Consumes: markers from Global Constraints.
- Produces: `parse_build_output(text: str, number_of_files, content_size, min_runs) -> list[dict]`; each dict has keys `mean, stddev, median, min, max, times, numberOfFiles, contentSize, minRuns, startTime, endTime` (`startTime`/`endTime` are `int|None`). `Results.parse_test(framework_test, test_type) -> {'results': list[dict]}`.

- [ ] **Step 1: Fixtures**

`tests/fixtures/raw_ok.txt` (note the build noise around the markers):

```
Generating 10 posts in content/post
SSGBERK_VERIFY_OK expected=10 got=10
STARTTIME 1790000000
Benchmark 1: hugo
  Time (abs ≡):        0.120 s
SSGBERK_RESULT_BEGIN
{"results":[{"command":"hugo","mean":0.12,"stddev":null,"median":0.12,"user":0.1,"system":0.02,"min":0.12,"max":0.12,"times":[0.12],"exit_codes":[0]}]}
SSGBERK_RESULT_END
ENDTIME 1790000001
```

`tests/fixtures/dool.csv`: generate a real one, do not hand-write it:

```bash
docker run --rm ubuntu:24.04 bash -c '
  apt-get -qq update >/dev/null && apt-get -qq install -y curl python3 >/dev/null &&
  cd /tmp && curl -LSs https://github.com/scottchiefbaker/dool/archive/v1.3.8.tar.gz | tar --strip-components=1 -xz &&
  ./install.py >/dev/null && dool -Tcm --output /tmp/d.csv 1 3 >/dev/null; cat /tmp/d.csv' > tests/fixtures/dool.csv
head -8 tests/fixtures/dool.csv
```

- [ ] **Step 2: Failing tests** — `tests/test_results.py`:

```python
import pathlib

from toolset.utils.results import Results, parse_build_output

FIX = pathlib.Path(__file__).parent / "fixtures"


def test_parses_hyperfine_json():
    [r] = parse_build_output((FIX / "raw_ok.txt").read_text(), "10", "0.500", "1")
    assert r["mean"] == 0.12 and r["times"] == [0.12] and r["stddev"] is None
    assert (r["numberOfFiles"], r["contentSize"], r["minRuns"]) == ("10", "0.500", "1")
    assert (r["startTime"], r["endTime"]) == (1790000000, 1790000001)


def test_missing_markers_is_failure():
    assert parse_build_output("Benchmark 1: hugo\n", "10", "0.500", "1") == []


def test_invalid_json_is_failure():
    text = "SSGBERK_RESULT_BEGIN\n{not json\nSSGBERK_RESULT_END\n"
    assert parse_build_output(text, "10", "0.500", "1") == []


def test_empty_results_array_is_failure():
    text = 'SSGBERK_RESULT_BEGIN\n{"results":[]}\nSSGBERK_RESULT_END\n'
    assert parse_build_output(text, "10", "0.500", "1") == []


def test_verify_fail_wins_over_valid_json():
    text = "SSGBERK_VERIFY_FAIL expected=10 got=0\n" + (FIX / "raw_ok.txt").read_text()
    assert parse_build_output(text, "10", "0.500", "1") == []


def test_parse_stats_reads_dool_csv(fake_benchmarker, tmp_path):
    fake_benchmarker.tests = []
    res = Results(fake_benchmarker)
    stats_file = res.get_stats_file("hugo", "datarate")
    pathlib.Path(stats_file).write_text((FIX / "dool.csv").read_text())
    stats = res._Results__parse_stats(type("T", (), {"name": "hugo"})(), "datarate", 0, 10**10, 1)
    assert stats, "expected at least one sampled row"
    first = next(iter(stats.values()))
    assert any("cpu" in k for k in first)
```

`tests/test_docker_helper.py`:

```python
import types
from unittest import mock

from toolset.utils import docker_helper


def test_benchmark_writes_raw_chunks_verbatim(tmp_path):
    chunks = [b'SSGBERK_RESULT_BEGIN\n{"results":[{"mean":12.', b'34}]}\nSSGBERK_RESULT_END\n']
    container = mock.Mock()
    container.logs.return_value = iter(chunks)
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.server = mock.Mock()
    helper.server.containers.run.return_value = container
    raw = tmp_path / "raw.txt"
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(raw))
    assert '"mean":12.34}' in raw.read_text()
```

- [ ] **Step 3: Run** — `.venv/bin/pytest tests/test_results.py tests/test_docker_helper.py -q` → FAIL (`ImportError: cannot import name 'parse_build_output'`, and the chunk test shows `12.\n34`).

- [ ] **Step 4: Implement**

In `toolset/utils/results.py`, add at module level (after imports):

```python
RESULT_BEGIN = 'SSGBERK_RESULT_BEGIN'
RESULT_END = 'SSGBERK_RESULT_END'
VERIFY_FAIL = 'SSGBERK_VERIFY_FAIL'


def parse_build_output(text, number_of_files, content_size, min_runs):
    '''
    Extracts the hyperfine JSON printed by build.sh between the result
    markers. Returns [] when the build failed verification or produced
    no parseable result.
    '''
    if VERIFY_FAIL in text:
        return []
    start = text.find(RESULT_BEGIN)
    end = text.find(RESULT_END, start)
    if start == -1 or end == -1:
        return []
    try:
        result = json.loads(text[start + len(RESULT_BEGIN):end])['results'][0]
    except (ValueError, KeyError, IndexError, TypeError):
        return []
    start_time = re.search(r'^STARTTIME (\d+)', text, re.M)
    end_time = re.search(r'^ENDTIME (\d+)', text, re.M)
    return [{
        'mean': result.get('mean'),
        'stddev': result.get('stddev'),
        'median': result.get('median'),
        'min': result.get('min'),
        'max': result.get('max'),
        'times': result.get('times', []),
        'numberOfFiles': number_of_files,
        'contentSize': content_size,
        'minRuns': min_runs,
        'startTime': int(start_time.group(1)) if start_time else None,
        'endTime': int(end_time.group(1)) if end_time else None,
    }]
```

Replace the whole body of `Results.parse_test` with:

```python
        raw_file = self.get_raw_file(framework_test.name, test_type)
        text = ''
        if os.path.exists(raw_file):
            with open(raw_file, encoding='utf-8', errors='replace') as raw_data:
                text = raw_data.read()
        results = {'results': parse_build_output(
            text, self.config.number_of_files, self.config.content_size,
            self.config.min_runs)}

        stats = []
        stats_path = self.get_stats_file(framework_test.name, test_type)
        has_stats = os.path.exists(stats_path) and os.path.getsize(stats_path) > 0
        for r in results['results']:
            if has_stats and r['startTime'] and r['endTime']:
                stats.append(self.__parse_stats(framework_test, test_type,
                                                r['startTime'], r['endTime'], 1))
        with open(stats_path + ".json", "w") as stats_file:
            json.dump(stats, stats_file, indent=2)

        return results
```

Replace the header handling at the top of `__parse_stats` (the `for _ in range(4): stats.next()` … `sub_header = ...` lines) with a header search that works for dool and dstat:

```python
        with open(stats_file) as stats:
            rows = list(csv.reader(stats))

        def is_number(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        # 'epoch' appears in both header rows; the sub header is the one
        # immediately followed by a numeric data row.
        header_index = next(
            (i for i, row in enumerate(rows)
             if 'epoch' in row and i > 0 and i + 1 < len(rows)
             and len(rows[i + 1]) > row.index('epoch')
             and is_number(rows[i + 1][row.index('epoch')])),
            None)
        if header_index is None:
            return stats_dict
        main_header = rows[header_index - 1]
        sub_header = rows[header_index]
        time_row = sub_header.index("epoch")
        int_counter = 0
        for row in rows[header_index + 1:]:
            if len(row) != len(sub_header):
                continue
```

and keep the rest of the loop body as is, dedented one level (it is no longer inside `with`). If dool's `main_header` row is shorter than `sub_header`, pad it: `main_header = main_header + [''] * (len(sub_header) - len(main_header))`. Inside the loop, convert with `float(column)` only when `column.strip()` is not empty; otherwise store `None`.

In `docker_helper.DockerHelper.benchmark`, replace `watch_container` with:

```python
        def watch_container(container):
            with open(raw_file, 'w', encoding='utf-8') as benchmark_file:
                for chunk in container.logs(stream=True):
                    text = chunk.decode('utf-8', 'replace')
                    benchmark_file.write(text)
                    benchmark_file.flush()
                    log(text)
```

and keep the command as `"/bin/bash ./%s" % (script)` (no `&`).

In `toolset/benchmark/benchmarker.py` `__begin_logging`, rename `dstat_string` → `dool_string` and the command word `dstat` → `dool` (same flags as upstream TechEmpower: `-Tafilmprs --aio --fs --ipc --lock --socket --tcp --raw --udp --unix --vm --disk-util --rpc --rpcd --output {output_file}`).

- [ ] **Step 5: Run** — `.venv/bin/pytest -q && .venv/bin/ruff check toolset tests` → all PASS.

- [ ] **Step 6: Commit** — `git add toolset tests && git commit -m "fix(results): parse hyperfine JSON from build.sh markers" -m "Record mean/stddev/median/min/max/times per generator instead of the inherited wrk parser. Write container output verbatim so chunked logs cannot corrupt the JSON. Switch resource stats to dool." -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

### Task 4: Toolset image, launcher and image names

**Files:**
- Modify: `Dockerfile`, `ssgberk`, `toolset/utils/docker_helper.py` (tags + filters), `toolset/utils/benchmark_config.py` (no change expected; verify), `toolset/utils/scaffolding.py` and `toolset/scaffolding/*` (any `matheusrv` text)
- Test: `tests/test_docker_helper.py` (add)

**Interfaces:**
- Produces: image `ssgberk/toolset`; generator images `ssgberk/test.<name>`; `DockerHelper.is_ssgberk_test_image(tag: str) -> bool` (staticmethod) used by `clean` and `__stop_all`.

- [ ] **Step 1: Failing test** — append to `tests/test_docker_helper.py`:

```python
import pytest


@pytest.mark.parametrize("tag,expected", [
    ("ssgberk/test.hugo:latest", True),
    ("ssgberk/toolset:latest", False),
    ("matheusrv/ssgberk.test.hugo:latest", False),
    ("nginx:latest", False),
])
def test_is_ssgberk_test_image(tag, expected):
    assert docker_helper.DockerHelper.is_ssgberk_test_image(tag) is expected
```

- [ ] **Step 2: Run** → FAIL `AttributeError: ... is_ssgberk_test_image`.

- [ ] **Step 3: Implement**

`docker_helper.py`:

```python
TEST_IMAGE_PREFIX = 'ssgberk/test.'
```

```python
    @staticmethod
    def is_ssgberk_test_image(tag):
        return tag.startswith(TEST_IMAGE_PREFIX)
```

Use `"%s%s" % (TEST_IMAGE_PREFIX, test.name)` everywhere `"matheusrv/ssgberk.test.%s"` appears (build tag, run image, benchmark image). In `clean()`: remove image when `DockerHelper.is_ssgberk_test_image(image.tags[0])`. In `__stop_all`: stop when `len(container.image.tags) > 0 and DockerHelper.is_ssgberk_test_image(container.image.tags[0])`.

`Dockerfile` (full replacement):

```dockerfile
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG DOOL_VERSION=v1.3.8

# WARNING: DON'T PUT A SPACE AFTER ANY BACKSLASH OR APT WILL BREAK
RUN apt-get -yqq update && apt-get -yqq install --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
      ca-certificates cloc curl git \
      python3 python3-colorama python3-pip python3-psutil python3-requests && \
    pip3 install --break-system-packages docker==7.1.0 && \
    rm -rf /var/lib/apt/lists/*

# Collect resource usage statistics
WORKDIR /tmp/dool
RUN curl -LSs "https://github.com/scottchiefbaker/dool/archive/${DOOL_VERSION}.tar.gz" | \
      tar --strip-components=1 -xz && \
    ./install.py && \
    rm -rf /tmp/dool

# The repository is bind-mounted with the host user's ownership
RUN git config --system --add safe.directory '*'

ENV PYTHONPATH=/FrameworkBenchmarks FWROOT=/FrameworkBenchmarks
WORKDIR /FrameworkBenchmarks

ENTRYPOINT ["python3", "/FrameworkBenchmarks/toolset/run-tests.py"]
```

`ssgberk` (last two lines): replace `matheusrv/ssgberk` with `ssgberk/toolset` in both the `docker build -t` and the `docker run` lines.

Then: `grep -rn matheusrv toolset ssgberk Dockerfile` must print nothing (README is Task 5).

- [ ] **Step 4: Run unit tests and the real launcher**

```bash
.venv/bin/pytest -q
./ssgberk --list-tests
```

Expected: pytest all pass. `--list-tests` builds `ssgberk/toolset` and prints the generator names found in `frameworks/` (still the 2019 set: cuttlebelle, gatsby, harp-ejs, …) and exits 0 with no traceback. (`--list-tests` doesn't build generator images, so old dockerfiles don't matter yet.)

- [ ] **Step 5: Commit** — `git add Dockerfile ssgberk toolset tests && git commit -m "build(toolset): ubuntu 24.04 + python 3 image, rename images to ssgberk/*" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

### Task 5: CI, changed-generator detection, Vagrant, README, package.json

**Files:**
- Create: `.github/workflows/ci.yml`, `toolset/github_actions/__init__.py`, `toolset/github_actions/github_actions_diff.py`
- Delete: `.travis.yml`, `toolset/travis/`
- Modify: `deployment/vagrant/core.rb`, `deployment/vagrant/bootstrap.sh`, `toolset/continuous/tfb-startup.sh`, `toolset/continuous/tfb-shutdown.sh`, `README.md`, `package.json`
- Test: `tests/test_github_actions_diff.py`

**Interfaces:**
- Produces: `changed_tests(changed_files: list[str], all_test_dirs: list[str], canonical_build_sh: str = "Go/hugo/build.sh") -> list[str]` in `toolset/github_actions/github_actions_diff.py`; CLI `python3 toolset/github_actions/github_actions_diff.py --base <ref> --repo <path>` prints one test dir (`Lang/name`) per line. Used by SF CI in Task 22.

- [ ] **Step 1: Failing tests** — `tests/test_github_actions_diff.py`:

```python
from toolset.github_actions.github_actions_diff import changed_tests

ALL = ["Go/hugo", "Ruby/jekyll", "Rust/zola"]


def test_only_touched_generators():
    assert changed_tests(["Ruby/jekyll/Gemfile", "README.md"], ALL) == ["Ruby/jekyll"]


def test_canonical_build_sh_runs_all():
    assert changed_tests(["Go/hugo/build.sh"], ALL) == ALL


def test_deleted_generator_is_skipped():
    assert changed_tests(["JavaScript/harp-ejs/build.sh"], ALL) == []


def test_ci_files_run_all():
    assert changed_tests([".github/workflows/ci.yml"], ALL) == ALL
```

- [ ] **Step 2: Run** → FAIL `ModuleNotFoundError`.

- [ ] **Step 3: Implement** `toolset/github_actions/github_actions_diff.py`:

```python
#!/usr/bin/env python3
'''
Prints the generator directories (Lang/name) a CI run must smoke-test,
given the files changed against a base ref in an ssg-frameworks checkout.
Changes to the canonical build.sh or to CI config run every generator.
'''
import argparse
import glob
import os
import subprocess
import sys


def changed_tests(changed_files, all_test_dirs, canonical_build_sh="Go/hugo/build.sh"):
    if any(f == canonical_build_sh or f.startswith(".github/") for f in changed_files):
        return list(all_test_dirs)
    touched = {"/".join(f.split("/")[:2]) for f in changed_files if f.count("/") >= 2}
    return [d for d in all_test_dirs if d in touched]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args(argv)
    files = subprocess.check_output(
        ["git", "diff", "--name-only", "%s...HEAD" % args.base],
        cwd=args.repo, text=True).split()
    all_dirs = sorted(
        os.path.dirname(os.path.relpath(p, args.repo))
        for p in glob.glob(os.path.join(args.repo, "*", "*", "benchmark_config.json")))
    for d in changed_tests(files, all_dirs):
        print(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`.github/workflows/ci.yml`:

```yaml
name: ci
on:
  push:
    branches: [master]
  pull_request:

jobs:
  toolset:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: python -m compileall -q toolset
      - run: ruff check toolset tests
      - run: pytest -q
```

(The end-to-end smoke job is added in Task 23, once the submodule points at the modernized generators.)

Delete `.travis.yml` and `toolset/travis/` with `git rm -r`.

`toolset/continuous/tfb-startup.sh` and `tfb-shutdown.sh`: add `export LANG=C.UTF-8` as line 2 (after the shebang), matching the monorepo.

Vagrant: in `deployment/vagrant/core.rb` set both `override.vm.box` values to `"bento/ubuntu-24.04"`. In `bootstrap.sh` replace the docker install block with the official repo method:

```bash
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -yqq
  sudo apt-get install -yqq docker-ce docker-ce-cli containerd.io
```

and change `ssgberk --mode verify --test gemini` in the motd to `ssgberk --test hugo -nf 10`.

`package.json`: remove the whole `"dependencies"` object; set `"repository": "https://github.com/ssgberk/benchmark-tool.git"`, `"version": "0.9.0"`, `"author": "Matheus Breguêz <matbrgz@gmail.com>"`.

`README.md` (both English and Portuguese sections, same edits in each):
- Replace the badge `<p>` block with: PRs welcome badge, `https://img.shields.io/github/actions/workflow/status/ssgberk/benchmark-tool/ci.yml?branch=master&style=flat-square` (CI), last-commit badge — all pointing to `ssgberk/benchmark-tool`. Drop Travis, Docker Hub, Scrutinizer, maintenance-2018 badges.
- Every `MatheusRV/StaticSiteGeneratorBenchmarks` / `matheusrv/StaticSiteGeneratorBenchmarks` → `ssgberk/benchmark-tool`; clone command → `git clone --recurse-submodules https://github.com/ssgberk/benchmark-tool.git`.
- `matheusrv/ssgberk` → `ssgberk/toolset`; `--mode verify --test gemini` and `--test gemini` → `--test hugo -nf 10`.
- Add a section "Measurement notes" / "Notas de medição" with the three bullets from spec §8 (bundler-dominated JS generators; Docker Desktop on macOS is for validation, publish numbers from native Linux; large `-nf` scenarios generate content slowly in bash).
- Add a "Content size" table with the `-cs` → KB mapping from Global Constraints.
- Keep the TechEmpower credit sentence.

- [ ] **Step 4: Run** — `.venv/bin/pytest -q && .venv/bin/ruff check toolset tests && grep -rn "matheusrv\|travis" README.md package.json toolset ssgberk Dockerfile deployment` → tests pass; grep prints nothing.

- [ ] **Step 5: Commit** — `git add -A .github toolset deployment README.md package.json .travis.yml && git commit -m "ci: replace travis with github actions; refresh vagrant and docs" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

---

## Phase B — `ssg-frameworks` (all paths relative to SF unless noted; commits happen in SF)

### Task 6: Canonical `build.sh` + Hugo end-to-end

**Files (SF):**
- Create: `Go/hugo/build.sh` (canonical), `tools/check-build-sh.sh`, `tests/build_sh/test_build_sh.sh`, `.gitignore`
- Modify: `Go/hugo/hugo.dockerfile`, `Go/hugo/benchmark_config.json`, `Go/hugo/src/config.toml`, `Go/hugo/README.md`; copy newer `src/` from monorepo where it differs (`/Users/jobs/Dev/ssgberk/StaticSiteGeneratorBenchmark/frameworks/Go/hugo/src`)

**Interfaces:**
- Consumes: env vars from `DatarateTestType.get_script_variables()`: `number_of_files`, `content_size`, `min_runs`, `verbose_build` (strings; `verbose_build` is `"True"`/`"False"` from Python bool → treat `True|true` as true).
- Produces: `benchmark_config.json` schema used by every generator task:
  ```json
  {
    "framework": "<name>",
    "tests": [{"default": {"approach": "Realistic", "classification": "Micro", "framework": "<name>",
                "language": "<Lang>", "display_name": "<name>", "notes": "", "versus": "<lang-lower>"}}],
    "content": [{"folder": "<dir>", "type": "3minus|3plus|2dot|none", "extension": "md"}],
    "config": [{"metadata_dateslug": "date", "metadata_layout": "", "build_command": "<cmd>",
                "build_verbose": "<cmd>", "output_folder": "<dir>", "output_glob": "<find -path pattern>",
                "cache_folders": ["<dir>", "..."]}]
  }
  ```
  `output_glob` is matched with `find <output_folder> -type f -path "<output_folder>/<output_glob>"`. `cache_folders` is optional.

- [ ] **Step 1: Write the shell test** — `tests/build_sh/test_build_sh.sh` runs `Go/hugo/build.sh` against a fake generator whose "build command" is a tiny shell script, inside `ubuntu:24.04` with jq/moreutils/hyperfine:

```bash
#!/bin/bash
# Usage: tests/build_sh/test_build_sh.sh   (from SF root; needs docker)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
docker run --rm -v "$ROOT":/sf -w /work ubuntu:24.04 bash -c '
set -euo pipefail
apt-get -qq update >/dev/null && apt-get -qq install -y --no-install-recommends jq moreutils curl ca-certificates >/dev/null
ARCH=$(dpkg --print-architecture)
curl -fsSL -o /tmp/h.deb https://github.com/sharkdp/hyperfine/releases/download/v1.20.0/hyperfine_1.20.0_${ARCH}.deb && dpkg -i /tmp/h.deb >/dev/null
fail() { echo "FAIL: $*"; exit 1; }

setup() {
  rm -rf /work/* && mkdir -p /work/posts && cd /work
  cp /sf/Go/hugo/build.sh .
  echo keep > posts/_index.md
  echo old > posts/2014-01-01-sample.md
  # fake generator: one html per post into out/posts/<name>.html, plus an index.html
  cat > gen.sh <<"EOF"
#!/bin/bash
mkdir -p out/posts; for f in posts/[0-9]*.md; do b=$(basename "$f" .md); echo "<h1>$b</h1>" > "out/posts/$b.html"; done; echo idx > out/index.html
[ -f out/stale.marker ] && echo "STALE_OUTPUT_SEEN"; touch out/stale.marker
EOF
  chmod +x gen.sh
  cat > benchmark_config.json <<EOF
{"framework":"fake","tests":[{"default":{}}],
 "content":[{"folder":"posts","type":"$1","extension":"md"}],
 "config":[{"metadata_dateslug":"date","metadata_layout":"","build_command":"./gen.sh","build_verbose":"",
            "output_folder":"out","output_glob":"$2"}]}
EOF
}

# test_verify_counts_exact + happy path + markers
setup 3minus "posts/*.html"
out=$(number_of_files=5 content_size=0.500 min_runs=2 verbose_build=True bash build.sh)
echo "$out" | grep -q "SSGBERK_VERIFY_OK expected=5 got=5" || fail "verify ok line"
echo "$out" | grep -q "^SSGBERK_RESULT_BEGIN$" || fail "begin marker"
echo "$out" | grep -q "^SSGBERK_RESULT_END$" || fail "end marker"
echo "$out" | grep -qE "^STARTTIME [0-9]+$" || fail "starttime"
echo "$out" | grep -qE "^ENDTIME [0-9]+$" || fail "endtime"
echo "$out" | sed -n "/^SSGBERK_RESULT_BEGIN$/,/^SSGBERK_RESULT_END$/p" | sed "1d;\$d" | jq -e ".results[0].times | length == 2" >/dev/null || fail "json times"
# prepare wipes output before each timed run (verbose => --show-output, so gen.sh output is visible)
echo "$out" | grep -q STALE_OUTPUT_SEEN && fail "output not cleaned between runs"

# test_reset_removes_only_dated_entries
[ -f posts/_index.md ] || fail "_index.md must survive"
[ ! -e posts/2014-01-01-sample.md ] || fail "sample post must be removed"
[ -z "$(ls posts | grep -E "^[0-9]{4}-")" ] || fail "generated posts must be removed at end"

# glob that also matches index.html -> got > expected -> VERIFY_FAIL
setup 3minus "*.html"
out=$(number_of_files=5 content_size=0.500 min_runs=1 verbose_build=False bash build.sh || true)
echo "$out" | grep -q "SSGBERK_VERIFY_FAIL expected=5 got=6" || fail "over-count must fail"
echo "$out" | grep -q SSGBERK_RESULT_BEGIN && fail "no result after verify fail"

# test_content_size_unknown_fails
setup 3minus "posts/*.html"
out=$(number_of_files=1 content_size=7 min_runs=1 verbose_build=False bash build.sh 2>&1 || true)
echo "$out" | grep -q "unknown content_size" || fail "unknown cs must fail loudly"

# legacy [500] accepted and sizes are right
setup none "posts/*.html"
number_of_files=1 content_size="[500]" min_runs=1 verbose_build=False KEEP_CONTENT=1 bash build.sh >/dev/null
size=$(stat -c %s posts/[0-9]*.md); [ "$size" -gt 500000 ] || fail "500 => ~550KB, got $size"

# 3plus header
setup 3plus "posts/*.html"
number_of_files=1 content_size=0.500 min_runs=1 verbose_build=False KEEP_CONTENT=1 bash build.sh >/dev/null
head -1 posts/[0-9]*.md | grep -qx "+++" || fail "3plus header"
echo "ALL build.sh TESTS PASSED"
'
```

`KEEP_CONTENT=1` is a test-only switch: when set, `build.sh` skips the final cleanup so the test can inspect generated files.

- [ ] **Step 2: Run it against the old build.sh to see it fail**

```bash
cp /Users/jobs/Dev/ssgberk/StaticSiteGeneratorBenchmark/frameworks/Go/hugo/build.sh Go/hugo/build.sh
chmod +x tests/build_sh/test_build_sh.sh && tests/build_sh/test_build_sh.sh
```

Expected: `FAIL: verify ok line`.

- [ ] **Step 3: Write the canonical `Go/hugo/build.sh`** (full replacement):

```bash
#!/bin/bash
# SSGBerk canonical build.sh — every generator directory carries an identical copy.
# Inputs (env): number_of_files, content_size, min_runs, verbose_build
# Reads: ./benchmark_config.json   Prints: SSGBERK_* markers parsed by the toolset.
export LANG=C.UTF-8
set -u

for cmd in jq sponge hyperfine; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        echo "[ ERROR ] required command not installed: ${cmd}"
        exit 1
    fi
done

number_of_files="${number_of_files:-100}"
content_size="${content_size:-0.500}"
content_size="${content_size//[\[\]]/}"
min_runs="${min_runs:-3}"
verbose_build="${verbose_build:-false}"
case "${verbose_build}" in True|true|1) verbose_build=true ;; *) verbose_build=false ;; esac

cfg="${PWD}/benchmark_config.json"
build_command=$(jq -r '.config[0].build_command' "${cfg}")
build_verbose=$(jq -r '.config[0].build_verbose // ""' "${cfg}")
metadata_layout=$(jq -r '.config[0].metadata_layout // ""' "${cfg}")
metadata_dateslug=$(jq -r '.config[0].metadata_dateslug // "date"' "${cfg}")
output_folder=$(jq -r '.config[0].output_folder // ""' "${cfg}")
output_glob=$(jq -r '.config[0].output_glob // ""' "${cfg}")
cache_folders=$(jq -r '(.config[0].cache_folders // []) | join(" ")' "${cfg}")
content_type=$(jq -r '.content[0].type' "${cfg}")
content_folder=$(jq -r '.content[0].folder' "${cfg}")
content_extension=$(jq -r '.content[0].extension' "${cfg}")
[ -z "${build_verbose}" ] && build_verbose="${build_command}"

today=$(date +%F)
dated_pattern='[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-*'

# Remove generated (date-named) posts only; section index files survive.
reset_content()
{
    mkdir -p "${content_folder}"
    find "${content_folder}" -mindepth 1 -maxdepth 1 -name "${dated_pattern}" -exec rm -rf {} +
}

clean_output()
{
    [ -n "${output_folder}" ] && rm -rf "${output_folder}"
    for d in ${cache_folders}; do rm -rf "${d}"; done
    return 0
}

paragraph="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum euismod luctus massa. Pellentesque porta augue non varius semper. In vitae pulvinar dolor. Nunc erat sem, facilisis eu augue in, aliquam viverra magna. Quisque porttitor sodales diam, a vestibulum sem semper vel. Integer tempus quam eu ex egestas, sed auctor neque venenatis. Fusce mattis metus pellentesque iaculis euismod. Vestibulum a dictum lectus, a porta odio. Etiam sit amet lobortis lorem. Mauris iaculis ornare risus, at dictum nullam."

case "${content_size}" in
    0.500)  repetitions=1 ;;
    500)    repetitions=1000 ;;
    1000)   repetitions=2000 ;;
    5000)   repetitions=10000 ;;
    10000)  repetitions=20000 ;;
    100000) repetitions=200000 ;;
    *) echo "[ ERROR ] unknown content_size: ${content_size}"; exit 1 ;;
esac
content=$(yes "${paragraph}" | head -n "${repetitions}" | tr -d '\n')

header_for()
{
    local title="${1}"
    case "${content_type}" in
    3minus)
        printf -- '---\n'
        [ -n "${metadata_layout}" ] && printf '%s\n' "${metadata_layout}"
        printf '%s: %s\ntitle: "%s"\n---\n' "${metadata_dateslug}" "${today}" "${title}"
        ;;
    3plus)
        printf '+++\ntitle = "%s"\n%s = %s\n+++\n' "${title}" "${metadata_dateslug}" "${today}"
        ;;
    2dot)
        [ -n "${metadata_layout}" ] && printf '.. %s\n' "${metadata_layout}"
        printf '.. title: %s\n.. slug: %s\n.. %s: %s\n\n' "${title}" "${title}" "${metadata_dateslug}" "${today}"
        ;;
    none) ;;
    *) echo "[ ERROR ] unknown content type: ${content_type}" >&2; exit 1 ;;
    esac
}

reset_content
echo "Generating ${number_of_files} posts (${content_size} KB) in ${content_folder}"
for i in $(seq -w 1 "${number_of_files}"); do
    name="${today}-${i}"
    { header_for "${name}"; printf '%s\n' "${content}"; } | sponge "${content_folder}/${name}.${content_extension}"
done
[ "${verbose_build}" = true ] && ls -sh "${content_folder}"

if [ "${verbose_build}" = true ]; then
    command="${build_verbose}"
else
    command="${build_command}"
fi

# Untimed verification build: the site must contain exactly one page per post.
clean_output
eval "${command}" > /tmp/ssgberk-verify.log 2>&1
verify_status=$?
if [ "${verify_status}" -ne 0 ]; then
    cat /tmp/ssgberk-verify.log
    echo "SSGBERK_VERIFY_FAIL build exited ${verify_status}"
    [ -z "${KEEP_CONTENT:-}" ] && reset_content
    exit 1
fi
if [ -n "${output_folder}" ] && [ -n "${output_glob}" ]; then
    got=$(find "${output_folder}" -type f -path "${output_folder}/${output_glob}" | wc -l | tr -d ' ')
    if [ "${got}" -ne "${number_of_files}" ]; then
        cat /tmp/ssgberk-verify.log
        echo "SSGBERK_VERIFY_FAIL expected=${number_of_files} got=${got}"
        [ -z "${KEEP_CONTENT:-}" ] && reset_content
        exit 1
    fi
    echo "SSGBERK_VERIFY_OK expected=${number_of_files} got=${got}"
else
    echo "[ WARN ] output_folder/output_glob not set; skipping output verification"
fi

show_output=""
[ "${verbose_build}" = true ] && show_output="--show-output"
prepare_cmd="true"
if [ -n "${output_folder}" ] || [ -n "${cache_folders}" ]; then
    prepare_cmd="rm -rf ${output_folder} ${cache_folders}"
fi

echo "STARTTIME $(date +%s)"
hyperfine --time-unit second --min-runs "${min_runs}" --max-runs "${min_runs}" \
    --prepare "${prepare_cmd}" ${show_output} \
    --export-json /tmp/ssgberk-hyperfine.json "${command}"
hyperfine_status=$?
echo "ENDTIME $(date +%s)"
echo "Number of files: ${number_of_files} | content size: ${content_size} KB | runs: ${min_runs}"

if [ "${hyperfine_status}" -eq 0 ]; then
    echo "SSGBERK_RESULT_BEGIN"
    cat /tmp/ssgberk-hyperfine.json
    echo
    echo "SSGBERK_RESULT_END"
fi

[ -z "${KEEP_CONTENT:-}" ] && reset_content
exit "${hyperfine_status}"
```

Why the stale check works: `gen.sh` prints `STALE_OUTPUT_SEEN` only if `out/` survived from a previous build. The first test case runs with `verbose_build=True`, so hyperfine runs with `--show-output` and that line would reach the captured output if `--prepare` failed to remove `output_folder` between runs.

- [ ] **Step 4: Run** — `tests/build_sh/test_build_sh.sh` → `ALL build.sh TESTS PASSED`.

- [ ] **Step 5: `tools/check-build-sh.sh`**

```bash
#!/bin/bash
# Fails if any generator's build.sh differs from the canonical Go/hugo/build.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
status=0
for f in */*/build.sh; do
    if ! cmp -s Go/hugo/build.sh "$f"; then echo "differs: $f"; status=1; fi
done
exit $status
```

(It will fail until Task 13; that's expected. Do not copy build.sh into other generators in this task.)

- [ ] **Step 6: Hugo**

`Go/hugo/hugo.dockerfile`: skeleton with `<name>`=`hugo`, no RUNTIME block, GENERATOR block:

```dockerfile
ARG HUGO_VERSION=0.167.0
RUN ARCH="$(dpkg --print-architecture)" \
 && curl -fsSL -o /tmp/hugo.deb \
      "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-${ARCH}.deb" \
 && dpkg -i /tmp/hugo.deb && rm /tmp/hugo.deb && hugo version
```

`Go/hugo/src/`: start from the monorepo copy (`cp -R /Users/jobs/Dev/ssgberk/StaticSiteGeneratorBenchmark/frameworks/Go/hugo/src/. Go/hugo/src/`). In `config.toml`: rename to `hugo.toml` is NOT required; remove the `config = "config.toml"` line; set `disableKinds = ["taxonomy", "term", "RSS", "sitemap", "robotsTXT", "404"]` (keeps `page`, `home`, `section`); `baseURL = "/"` (Hugo ≥0.60 key casing). Replace deprecated template calls Hugo 0.167 rejects (check build output: `.Site.RSSLink`, `.Hugo`, `.RSSLink`, `.Data.Pages` → `.Site.RegularPages`, `.UniqueID`, `{{ template "_internal/..." }}` that no longer exist). Ensure `layouts/_default/single.html` renders `.Content`.

`Go/hugo/benchmark_config.json`: keep `tests`; `content`: `{"folder": "content/post", "type": "3minus", "extension": "md"}`; `config`: `{"metadata_dateslug": "date", "metadata_layout": "", "build_command": "hugo --quiet", "build_verbose": "hugo --logLevel debug", "output_folder": "public", "output_glob": "post/*/index.html", "cache_folders": ["resources/_gen"]}` (drop `layout: post` unless the theme uses it).

`Go/hugo/README.md`: one paragraph: generator, version, content folder, output glob, how to run (`./ssgberk --test hugo -nf 10`).

`.gitignore` (SF root): `node_modules/`, `public/`, `_site/`, `.DS_Store`.

- [ ] **Step 7: End-to-end** — run the Generator smoke procedure for `hugo`. Expected: pass; `got=10`.

- [ ] **Step 8: Commit (SF)** — `git add -A Go/hugo tools tests .gitignore && git commit -m "feat(hugo): canonical build.sh with result markers; hugo 0.167.0" -m "The previous config disabled the page kind, so hugo never rendered posts. Output verification now catches that." -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

### Tasks 7–12: update existing generators

Standard steps for every task in 7–12 and 14–21 (each its own checkbox when tracking):

- [ ] Copy `Go/hugo/build.sh` into the generator dir; confirm `tools/check-build-sh.sh` no longer lists it.
- [ ] Write the dockerfile from the skeleton with the task's RUNTIME/GENERATOR blocks.
- [ ] Write/refresh manifest; generate the lockfile inside the runtime image.
- [ ] Write `benchmark_config.json` with the task's exact `content`/`config`, and the site files.
- [ ] Run the Generator smoke procedure; iterate on template errors shown in `raw.txt` until it passes with `got == expected`.
- [ ] Update the generator `README.md` (version, content folder, output glob, run command).
- [ ] Commit in SF.

Details for 7–12: copy `Go/hugo/build.sh` into the generator dir; start `src/` from the monorepo copy (`/Users/jobs/Dev/ssgberk/StaticSiteGeneratorBenchmark/frameworks/<Lang>/<name>/src`) when it exists there; rewrite the dockerfile from the skeleton; update the manifest + regenerate the lockfile **inside the generator image** (so the lock matches Linux) with `docker run --rm -v "$PWD":/w -w /w <image-with-runtime> <npm install|bundle lock|composer update>`; set `benchmark_config.json` `content`/`config` exactly as given; remove the old `src` sample posts (`build.sh` also removes them at runtime, but don't ship them); run the smoke procedure; commit. Fix template incompatibilities the new major version reports in the verification build log (`/tmp/ssgberk-verify.log` is printed on failure).

#### Task 7: gatsby 5.16.1 (`JavaScript/gatsby`)

- `git rm -r --cached JavaScript/gatsby/node_modules && rm -rf JavaScript/gatsby/node_modules`.
- `package.json` dependencies: `"gatsby": "5.16.1"`, `"gatsby-source-filesystem": "^5"`, `"gatsby-transformer-remark": "^6"`, `"react": "^18.3.1"`, `"react-dom": "^18.3.1"`; remove eslint/typescript/gatsby-link/gatsby-plugin-catch-links. Scripts: `"build": "gatsby build"`, `"build-verbose": "gatsby build --verbose"`.
- `gatsby-config.js`: drop `pathPrefix` and `gatsby-plugin-catch-links`; point `gatsby-source-filesystem` at `${__dirname}/src/pages/posts`.
- `gatsby-node.js`: `createPages` querying `allMarkdownRemark { nodes { id fields { slug } } }` and creating `/posts/<slug>/` from `src/templates/post.js`; `onCreateNode` adds `slug` = file base name. Update `src/templates/post.js` to a function component with a `query` export by `id`.
- Dockerfile: Node RUNTIME; GENERATOR: `COPY package.json package-lock.json /opt/gatsby/src/` + `RUN npm ci` + `ENV GATSBY_TELEMETRY_DISABLED=1`.
- Config: content `{"folder":"src/pages/posts","type":"3minus","extension":"md"}` — move the content folder out of `src/pages` if gatsby tries to render `.md` as pages; use `content/posts` then and update the filesystem source path. `config`: `build_command: "npm run --silent build"`, `build_verbose: "npm run build-verbose"`, `output_folder: "public"`, `output_glob: "posts/*/index.html"`, `cache_folders: [".cache"]`.

#### Task 8: jigsaw v1.8.8 (`PHP/jigsaw`)

- RUNTIME: PHP only (drop the Node/yarn install and any mix/webpack assets from `src`):
  ```dockerfile
  RUN apt-get -yqq update && apt-get -yqq install --no-install-recommends software-properties-common gpg-agent \
   && add-apt-repository -y ppa:ondrej/php && apt-get -yqq update \
   && apt-get -yqq install --no-install-recommends php8.4-cli php8.4-mbstring php8.4-xml php8.4-curl php8.4-zip unzip \
   && rm -rf /var/lib/apt/lists/* \
   && curl -fsSL https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer
  ```
- `composer.json` at the generator root: `{"require": {"tightenco/jigsaw": "1.8.8"}}`; GENERATOR: `COPY composer.json composer.lock /opt/jigsaw/src/` + `RUN composer install --no-interaction --no-progress`. Build command `vendor/bin/jigsaw build` (not a global `jigsaw`).
- `config.php`: collection `posts` with `'path' => 'posts/{filename}'`; remove `baseUrl` subpath.
- Config: content `{"folder":"source/_posts","type":"3minus","extension":"md"}`, `metadata_layout: "extends: _layouts.post"`, `build_command: "vendor/bin/jigsaw build --quiet"`, `build_verbose: "vendor/bin/jigsaw build -v"`, `output_folder: "build_local"`, `output_glob: "posts/*/index.html"`, `cache_folders: ["cache"]`.

#### Task 9: nikola 8.3.3 (`Python/nikola-mako`)

- Python RUNTIME; `requirements.txt`: `Nikola[extras]==8.3.3`; GENERATOR: `COPY requirements.txt /opt/nikola/src/` + `RUN pip install --no-cache-dir -r requirements.txt` (move `requirements.txt` to the generator root and adjust the COPY path accordingly; skeleton's `COPY src/` stays).
- Remove `opentimestamps-client yuicompressor` (not needed).
- `conf.py`: `POSTS = (("posts/*.md", "posts", "post.tmpl"),)`, `PAGES = ()`, `COMPILERS["markdown"] = ('.md',)`, `OUTPUT_FOLDER = "output"`, `PRETTY_URLS = True`, disable RSS/sitemap/archives/tags if they add pages (they don't affect the post glob, but keep the build lean: `GENERATE_RSS = False`).
- Config: content `{"folder":"posts","type":"2dot","extension":"md"}`, `build_command: "nikola build -q"`, `build_verbose: "nikola build -v 2"`, `output_folder: "output"`, `output_glob: "posts/*/index.html"`, `cache_folders: ["cache", ".doit.db", ".doit.db.dat", ".doit.db.dir", ".doit.db.bak"]` (nikola's doit state would make runs incremental).

#### Task 10: jekyll 4.4.1 (`Ruby/jekyll`)

- Ruby RUNTIME; `Gemfile` (generator root): `source "https://rubygems.org"` + `gem "jekyll", "4.4.1"`; `bundle lock` inside the image → `Gemfile.lock`; GENERATOR: `COPY Gemfile Gemfile.lock /opt/jekyll/src/` + `RUN bundle install`.
- `_config.yml`: `path: ''`, `url: ''`, `permalink: /posts/:title/`, `exclude: [build.sh, benchmark_config.json, Gemfile, Gemfile.lock, README.md]`.
- Config: content `{"folder":"_posts","type":"3minus","extension":"md"}`, `metadata_layout: "layout: post"`, `build_command: "bundle exec jekyll build --quiet"` (**no `--incremental`**), `build_verbose: "bundle exec jekyll build --verbose"`, `output_folder: "_site"`, `output_glob: "posts/*/index.html"`, `cache_folders: [".jekyll-cache", ".jekyll-metadata"]`.

#### Task 11: nanoc 4.14.8 (`Ruby/nanoc`)

- `Gemfile`: `gem "nanoc", "4.14.8"`, `gem "kramdown"`, `gem "erubi"`; `bundle lock` in image.
- Remove the `Gemfile` inside `src/` (monorepo has one there too) so there's a single Gemfile at `/opt/nanoc/src`.
- `Rules`: compile `/posts/*.md` with `filter :kramdown` + `layout '/post.*'`, route to `/posts/<basename>/index.html`; compile `/index.*` similarly; ignore other data.
- Config: content `{"folder":"content/posts","type":"3minus","extension":"md"}`, `metadata_dateslug: "created_at"`, `metadata_layout: "kind: article"`, `build_command: "bundle exec nanoc compile"`, `build_verbose: "bundle exec nanoc compile --verbose"`, `output_folder: "output"`, `output_glob: "posts/*/index.html"`, `cache_folders: ["tmp"]` (nanoc's checksum store would make runs incremental).

#### Task 12: middleman 4.6.3 (`Ruby/middleman`, from WIP)

- Start from `SF/Ruby/middleman` (it's WIP in the monorepo but already in SF at `Ruby/middleman`).
- `Gemfile`: `gem "middleman", "4.6.3"`, `gem "middleman-blog", "~> 4.0"`, `gem "webrick"`, `gem "tzinfo-data"`; drop `execjs`.
- `config.rb`: `activate :blog do |blog| blog.sources = "posts/{year}-{month}-{day}-{title}.html"; blog.permalink = "posts/{title}/index.html"; blog.layout = "post"; end`.
- Config: content `{"folder":"source/posts","type":"3minus","extension":"md"}`, `metadata_layout: ""`, `build_command: "bundle exec middleman build"`, `build_verbose: "bundle exec middleman build --verbose"`, `output_folder: "build"`, `output_glob: "posts/*/index.html"`, `cache_folders: [".sass-cache"]`.
- If native extensions fail on Ruby 3.2 after a genuine attempt, apply the `_wip/` fallback from the Generator smoke procedure.

### Task 13: metalsmith 2.7.0 handlebars + nunjucks; remove dead generators; build.sh check passes

**Files (SF):** `JavaScript/metalsmith-handlebars/*`, `JavaScript/metalsmith-nunjucks/*`; delete `JavaScript/harp-ejs`, `JavaScript/harp-jade`, `JavaScript/phenomic-react`, `JavaScript/cuttlebelle`, `Ruby/webgen`.

- [ ] **Step 1: Metalsmith (both variants; only the engine differs)**

`package.json` (handlebars; nunjucks swaps the last dep for `"jstransformer-nunjucks": "^1.2.0"`):

```json
{
  "name": "metalsmith-handlebars-sample",
  "private": true,
  "type": "module",
  "scripts": { "build": "node index.js" },
  "dependencies": {
    "metalsmith": "2.7.0",
    "@metalsmith/markdown": "^1.10.0",
    "@metalsmith/layouts": "^3.0.0",
    "@metalsmith/permalinks": "^3.2.0",
    "jstransformer-handlebars": "^1.2.0"
  }
}
```

`src/index.js`:

```js
import Metalsmith from 'metalsmith'
import markdown from '@metalsmith/markdown'
import permalinks from '@metalsmith/permalinks'
import layouts from '@metalsmith/layouts'
import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

Metalsmith(dirname(fileURLToPath(import.meta.url)))
  .source('./content')
  .destination('./build')
  .clean(true)
  .use(markdown())
  .use(permalinks({ pattern: ':title' }))
  .use(layouts({ directory: 'layouts', default: 'post.hbs' }))  // nunjucks: 'post.njk'
  .build((err) => { if (err) { console.error(err); process.exit(1) } })
```

Layout `src/layouts/post.hbs`: `<!doctype html><html><head><title>{{title}}</title></head><body><h1>{{title}}</h1>{{{contents}}}</body></html>` (nunjucks `post.njk`: same with `{{ title }}` and `{{ contents | safe }}`). Content dir `src/content/posts/` with a `.gitkeep`. Permalink `:title` gives `build/posts/<title>/index.html` because the source path is `posts/…` — if `@metalsmith/permalinks` v3 flattens, use `pattern: 'posts/:title'`.

Drop `Makefile`, `lighttpd.conf`, old deps. Node RUNTIME; `package.json`/`package-lock.json` live at the generator root; GENERATOR: `COPY package.json package-lock.json /opt/<name>/src/` + `RUN npm ci`.

Config: content `{"folder":"content/posts","type":"3minus","extension":"md"}`, `metadata_layout: ""`, `build_command: "node index.js"`, `output_folder: "build"`, `output_glob: "posts/*/index.html"`.

Smoke both (`metalsmith-handlebars`, `metalsmith-nunjucks`), commit each.

- [ ] **Step 2: Remove dead generators**

```bash
git rm -r -q JavaScript/harp-ejs JavaScript/harp-jade JavaScript/phenomic-react JavaScript/cuttlebelle Ruby/webgen
git commit -m "chore: remove unmaintained generators (harp, phenomic, cuttlebelle, webgen)" -m "Harp was rewritten and abandoned, Phenomic is archived, Cuttlebelle has been inactive since 2023, webgen has no meaningful usage." -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 3: Verify** — `tools/check-build-sh.sh` exits 0 (every remaining `*/*/build.sh` equals the canonical one; copy it where missing).

### Tasks 14–21: new generators

Same procedure as Tasks 7–12: skeleton dockerfile, `build.sh` copied from `Go/hugo/build.sh`, manifest + lockfile generated inside the runtime image, smoke procedure, one commit per generator (`feat(<name>): add <name> <version>`). Every site: base layout, post template, index listing posts. Each section below gives the exact files.

#### Task 14: zola 0.23.6 (`Rust/zola`)

Dockerfile: no RUNTIME; GENERATOR:

```dockerfile
ARG ZOLA_VERSION=0.23.6
RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in amd64) ZARCH=x86_64 ;; arm64) ZARCH=aarch64 ;; esac \
 && curl -fsSL "https://github.com/getzola/zola/releases/download/v${ZOLA_VERSION}/zola-v${ZOLA_VERSION}-${ZARCH}-unknown-linux-gnu.tar.gz" \
    | tar -xz -C /usr/local/bin && zola --version
```

`src/config.toml`:

```toml
base_url = "/"
title = "SSGBerk Zola"
compile_sass = false
build_search_index = false
generate_feeds = false
```

`src/content/posts/_index.md`:

```
+++
title = "Posts"
sort_by = "date"
+++
```

`src/templates/base.html`: `<!doctype html><html><head><title>{% block title %}{{ config.title }}{% endblock %}</title></head><body>{% block content %}{% endblock %}</body></html>`
`src/templates/index.html`: extends base; lists `{% set s = get_section(path="posts/_index.md") %}{% for p in s.pages %}<a href="{{ p.permalink }}">{{ p.title }}</a>{% endfor %}`.
`src/templates/section.html`: extends base; same loop over `section.pages`.
`src/templates/page.html`: extends base; `<h1>{{ page.title }}</h1>{{ page.content | safe }}`.

Config: content `{"folder":"content/posts","type":"3plus","extension":"md"}`, `build_command: "zola build"`, `output_folder: "public"`, `output_glob: "posts/*/index.html"`, `versus: "rust"`, `language: "Rust"`.

Note: zola strips a leading `YYYY-MM-DD-` from filenames for the slug (`2026-10-04-001.md` → `posts/001/`) — glob still matches.

#### Task 15: astro 7.3.5 (`JavaScript/astro`)

`package.json`: `{"name":"astro-sample","private":true,"type":"module","scripts":{"build":"astro build"},"dependencies":{"astro":"7.3.5"}}` + `ENV ASTRO_TELEMETRY_DISABLED=1`.
`src/astro.config.mjs`: `import { defineConfig } from 'astro/config'; export default defineConfig({ trailingSlash: 'always', build: { format: 'directory' } });`
`src/src/content.config.ts` — content collection with the glob loader (check `node_modules/astro` types for the v7 import path of `z`; in v5 it was `astro:content`, later versions export it from `astro/zod`):

```ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const posts = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/posts' }),
  schema: z.object({ title: z.string(), date: z.coerce.date() }),
});

export const collections = { posts };
```

`src/src/pages/index.astro`: `getCollection('posts')` → list links `/posts/${p.id}/`.
`src/src/pages/posts/[id].astro`: `getStaticPaths` from `getCollection('posts')`; `const { Content } = await render(post)`; render `<h1>{post.data.title}</h1><Content />`.
Config: content `{"folder":"src/content/posts","type":"3minus","extension":"md"}`, `build_command: "npx astro build --silent"`, `build_verbose: "npx astro build --verbose"`, `output_folder: "dist"`, `output_glob: "posts/*/index.html"`, `cache_folders: [".astro", "node_modules/.astro"]`.

#### Task 16: eleventy 3.1.6 (`JavaScript/eleventy`)

`package.json`: `{"name":"eleventy-sample","private":true,"type":"module","dependencies":{"@11ty/eleventy":"3.1.6"}}`.
`src/eleventy.config.js`:

```js
export default function (eleventyConfig) {
  eleventyConfig.ignores.add('README.md');
  return { dir: { input: '.', includes: '_includes', output: '_site' } };
}
```

`src/posts/posts.json`: `{"layout":"post.njk","tags":"posts","permalink":"/posts/{{ page.fileSlug }}/"}`
`src/_includes/post.njk`: `<!doctype html><html><head><title>{{ title }}</title></head><body><h1>{{ title }}</h1>{{ content | safe }}</body></html>`
`src/index.njk`: `---\npermalink: /\n---\n<ul>{% for p in collections.posts %}<li><a href="{{ p.url }}">{{ p.data.title }}</a></li>{% endfor %}</ul>`
Config: content `{"folder":"posts","type":"3minus","extension":"md"}`, `build_command: "npx @11ty/eleventy --quiet"`, `build_verbose: "DEBUG=Eleventy* npx @11ty/eleventy"`, `output_folder: "_site"`, `output_glob: "posts/*/index.html"`, `cache_folders: [".cache"]`.

Note: Eleventy also strips a leading date from `fileSlug` (`2026-10-04-001` → `001`); glob still matches.

#### Task 17: hexo 8.1.2 (`JavaScript/hexo`)

`package.json`: `{"name":"hexo-sample","private":true,"hexo":{"version":"8.1.2"},"dependencies":{"hexo":"8.1.2","hexo-renderer-marked":"^7.0.0","hexo-renderer-ejs":"^2.0.0","hexo-generator-index":"^4.0.0"}}`.
`src/_config.yml`:

```yaml
title: SSGBerk Hexo
url: http://localhost
permalink: posts/:title/
source_dir: source
public_dir: public
theme: minimal
new_post_name: :title.md
```

Theme `src/themes/minimal/layout/layout.ejs`: `<!doctype html><html><head><title><%= page.title || config.title %></title></head><body><%- body %></body></html>`; `post.ejs`: `<h1><%= page.title %></h1><%- page.content %>`; `index.ejs`: `<% page.posts.each(function(p){ %><a href="<%- url_for(p.path) %>"><%= p.title %></a><% }) %>`.
Config: content `{"folder":"source/_posts","type":"3minus","extension":"md"}`, `build_command: "npx hexo generate --silent"`, `build_verbose: "npx hexo generate --debug"`, `output_folder: "public"`, `output_glob: "posts/*/index.html"`, `cache_folders: ["db.json"]` (hexo's db.json makes runs incremental).

#### Task 18: next.js 16.3.8 static export (`JavaScript/nextjs-export`)

`package.json`: `{"name":"nextjs-export-sample","private":true,"scripts":{"build":"next build"},"dependencies":{"next":"16.3.8","react":"^19.2.0","react-dom":"^19.2.0","gray-matter":"^4.0.3","marked":"^16.0.0"}}` + `ENV NEXT_TELEMETRY_DISABLED=1`.
`src/next.config.mjs`: `export default { output: 'export', trailingSlash: true, images: { unoptimized: true } };`
`src/lib/posts.js`:

```js
import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';
import { marked } from 'marked';

const dir = path.join(process.cwd(), 'content/posts');

export function slugs() {
  return fs.readdirSync(dir).filter((f) => f.endsWith('.md')).map((f) => f.slice(0, -3));
}

export function post(slug) {
  const { data, content } = matter(fs.readFileSync(path.join(dir, `${slug}.md`), 'utf8'));
  return { title: data.title, html: marked.parse(content) };
}
```

`src/app/layout.js`: `export default function RootLayout({ children }) { return <html lang="en"><body>{children}</body></html>; }`
`src/app/page.js`: imports `slugs`, renders `<ul>` of `<a href={`/posts/${s}/`}>`.
`src/app/posts/[slug]/page.js`:

```js
import { slugs, post } from '../../../lib/posts';

export const dynamicParams = false;
export function generateStaticParams() { return slugs().map((slug) => ({ slug })); }

export default async function Post({ params }) {
  const { slug } = await params;
  const p = post(slug);
  return (<article><h1>{p.title}</h1><div dangerouslySetInnerHTML={{ __html: p.html }} /></article>);
}
```

`content/posts/.gitkeep`. If `generateStaticParams` returning `[]` breaks the build when the folder is empty, that's fine — build.sh always generates posts first.
Config: content `{"folder":"content/posts","type":"3minus","extension":"md"}`, `build_command: "npx next build"`, `output_folder: "out"`, `output_glob: "posts/*/index.html"`, `cache_folders: [".next"]`, `display_name: "next.js (export)"`.

#### Task 19: vitepress 1.6.4 (`JavaScript/vitepress`)

`package.json`: `{"name":"vitepress-sample","private":true,"type":"module","dependencies":{"vitepress":"1.6.4"}}`.
`src/.vitepress/config.mjs`: `export default { title: 'SSGBerk VitePress', srcExclude: ['README.md'] };`
`src/index.md`: `# Posts` + a `<script setup>` using `createContentLoader` is optional — keep it static: `# SSGBerk VitePress`.
`src/posts/.gitkeep`.
Config: content `{"folder":"posts","type":"3minus","extension":"md"}`, `build_command: "npx vitepress build ."`, `output_folder: ".vitepress/dist"`, `output_glob: "posts/*.html"`, `cache_folders: [".vitepress/cache"]`.

#### Task 20: pelican 4.12.0 (`Python/pelican`)

Python RUNTIME; `requirements.txt`: `pelican[markdown]==4.12.0`.
`src/pelicanconf.py`:

```python
AUTHOR = "SSGBerk"
SITENAME = "SSGBerk Pelican"
SITEURL = ""
PATH = "content"
OUTPUT_PATH = "output"
TIMEZONE = "UTC"
DEFAULT_LANG = "en"
ARTICLE_URL = "posts/{slug}/"
ARTICLE_SAVE_AS = "posts/{slug}/index.html"
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
DEFAULT_PAGINATION = False
MARKDOWN = {"extension_configs": {"markdown.extensions.meta": {}}}
```

`src/content/.gitkeep`. Python-Markdown's `meta` extension accepts the `---` YAML-style delimiters that `3minus` produces.
Config: content `{"folder":"content","type":"3minus","extension":"md"}`, `build_command: "pelican -q"`, `build_verbose: "pelican -v"`, `output_folder: "output"`, `output_glob: "posts/*/index.html"`, `cache_folders: ["cache", "__pycache__"]`.
If titles come out with literal quotes (`"2026-…"`) the slug still matches the glob; acceptable.

#### Task 21: mkdocs 1.6.1 (`Python/mkdocs`)

Python RUNTIME; `requirements.txt`: `mkdocs==1.6.1`.
`src/mkdocs.yml`: `site_name: SSGBerk MkDocs` / `docs_dir: docs` / `site_dir: site` / `use_directory_urls: true`.
`src/docs/index.md`: `# SSGBerk MkDocs`. `src/docs/posts/.gitkeep`.
Config: content `{"folder":"docs/posts","type":"none","extension":"md"}`, `build_command: "mkdocs build -q"`, `build_verbose: "mkdocs build -v"`, `output_folder: "site"`, `output_glob: "posts/*/index.html"`.

### Task 22: `ssg-frameworks` CI

**Files (SF):** `.github/workflows/ci.yml`, `README.md` (new, short), `LICENSE` (keep).

- [ ] **Step 1:** `.github/workflows/ci.yml`:

```yaml
name: ci
on:
  push:
    branches: [master]
  pull_request:

jobs:
  checks:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: tools/check-build-sh.sh
      - run: tests/build_sh/test_build_sh.sh

  changed:
    runs-on: ubuntu-24.04
    outputs:
      tests: ${{ steps.diff.outputs.tests }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          path: frameworks
      - uses: actions/checkout@v4
        with:
          repository: ssgberk/benchmark-tool
          path: bt
      - id: diff
        run: |
          base=${{ github.event.pull_request.base.sha || 'HEAD~1' }}
          tests=$(python3 bt/toolset/github_actions/github_actions_diff.py --base "$base" --repo frameworks \
                  | xargs -n1 basename | jq -R . | jq -cs .)
          echo "tests=$tests" >> "$GITHUB_OUTPUT"

  smoke:
    needs: changed
    if: needs.changed.outputs.tests != '[]'
    strategy:
      fail-fast: false
      matrix:
        test: ${{ fromJson(needs.changed.outputs.tests) }}
        runner: [ubuntu-24.04, ubuntu-24.04-arm]
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@v4
        with:
          repository: ssgberk/benchmark-tool
      - uses: actions/checkout@v4
        with:
          path: frameworks
      - run: ./ssgberk --test ${{ matrix.test }} -nf 10 -cs 0.500 -mr 1
      - run: |
          R=$(ls -td results/*/ | head -1)
          jq -e --arg t "${{ matrix.test }}" '.succeeded.datarate | index($t)' "$R/results.json"
          jq -e --arg t "${{ matrix.test }}" '.rawData.datarate[$t][0].mean > 0' "$R/results.json"
```

Note: `./ssgberk` uses `docker run -i -t` only when stdout is a TTY, so it works in Actions. Until `benchmark-tool`'s branch is merged, the `bt` checkout gets the old toolset; the `smoke` job is expected to fail on PRs opened before Phase A is merged — say so in the PR description.

- [ ] **Step 2:** `README.md` (SF): table of the 17 generators (language, name, version, content type, output glob) and "how to add a generator" (copy canonical `build.sh`, follow the dockerfile skeleton, set `output_folder`/`output_glob`, run `./ssgberk --test <name> -nf 10`).

- [ ] **Step 3:** `tools/check-build-sh.sh && tests/build_sh/test_build_sh.sh` → pass. Commit `ci: add build.sh checks and per-generator smoke tests`.

### Task 23: Submodule bump, full run, example results, smoke job (BT)

- [ ] **Step 1: Full local run** (BT):

```bash
./ssgberk --clean
./ssgberk -nf 100 -cs 500 -mr 3
R=$(ls -td results/*/ | head -1)
jq '.succeeded.datarate | length' "$R/results.json"    # Expected: 17 (minus any _wip fallbacks)
jq '.failed.datarate' "$R/results.json"                # Expected: []
jq -r '.rawData.datarate | to_entries[] | "\(.key)\t\(.value[0].mean)"' "$R/results.json" | sort -k2 -n
```

- [ ] **Step 2:** `mkdir -p docs/results && cp "$R/results.json" docs/results/example-2026-10.json`. Add a short `docs/results/README.md`: date, machine (`uname -m`, Docker version, CPU), command used, note that macOS numbers are for validation only.

- [ ] **Step 3: Submodule pointer** — the SF branch must exist on the remote before the pointer is useful to others; until the human pushes, record the commit locally:

```bash
SF_HEAD=$(git -C frameworks rev-parse HEAD)
git add frameworks
git ls-files -s frameworks    # Expected: 160000 <SF_HEAD> 0	frameworks
```

- [ ] **Step 4: Smoke job** — append to BT `.github/workflows/ci.yml`:

```yaml
  smoke:
    needs: toolset
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
      - run: ./ssgberk --test hugo -nf 10 -cs 0.500 -mr 1
      - run: |
          R=$(ls -td results/*/ | head -1)
          jq -e '.rawData.datarate.hugo[0].mean > 0' "$R/results.json"
```

- [ ] **Step 5: Commit (BT)** — `git add docs/results .github/workflows/ci.yml && git commit -m "chore: bump ssg-frameworks to modernized generators; add example results" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

- [ ] **Step 6: Final verification (BT)** — `.venv/bin/pytest -q && .venv/bin/ruff check toolset tests && (cd frameworks && tools/check-build-sh.sh)`; all pass.

Worktree cleanup (`git worktree remove` + `git worktree prune` in both repos) happens only after the human decides how to integrate (push/PR/merge) — not in this task.
