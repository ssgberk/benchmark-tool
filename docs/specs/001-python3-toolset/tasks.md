# Python 3 Toolset — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the `ssgberk` toolset image and launcher build and run on Ubuntu 24.04 + Python 3 with Docker 29: port Python 2→3, rename images to `ssgberk/*`, fix the CLI flags, and replace Travis with GitHub Actions.

**Architecture:** Minimal Python 2→3 port of the TechEmpower-derived toolset in `ssgberk/benchmark-tool`, keeping the inherited structure (`toolset/benchmark`, `toolset/utils`, scaffolding, audit, continuous, vagrant). No functional change to results parsing here (that is `docs/specs/002-hyperfine-results`).

**Tech Stack:** Python 3.12 (toolset image) / 3.14 (host dev), docker-py 7.1.0, pytest, ruff, dool 1.3.8, Ubuntu 24.04, GitHub Actions.

**Spec:** `docs/specs/001-python3-toolset/spec.md` and `docs/specs/001-python3-toolset/plan.md` (same directory, repo `ssgberk/benchmark-tool`). Read both before starting any task.

In this file **BT** = `/Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize` (repo `ssgberk/benchmark-tool`, branch `chore/modernize-2026`) and **SF** = `BT/frameworks` (repo `ssgberk/ssg-frameworks`, branch `chore/modernize-2026`). Layout: `docs/specs/ROADMAP.md` in BT.

## Global Constraints

- Git author/committer `Matheus Breguêz <matbrgz@gmail.com>`; every commit GPG-signed (repo config already has `commit.gpgsign=true`, key `B6FA8458D5176E83`). Never use `--no-gpg-sign` or `--author`.
- Every commit message ends with the trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Never commit to `master`. Never push, open PRs, or close dependabot branches unless the human explicitly asks.
- Toolset image tag: `ssgberk/toolset`. Generator image tag: `ssgberk/test.<name>`. No `matheusrv` strings may remain in `toolset/`, `ssgberk`, or `Dockerfile`.
- Pinned versions: hyperfine `1.20.0`, dool `v1.3.8`, docker-py `7.1.0`, Node `24.21.0`, hugo `0.167.0`, zola `0.23.6`, jekyll `4.4.1`, nanoc `4.14.8`, middleman `4.6.3`, nikola `8.3.3`, pelican `4.12.0`, mkdocs `1.6.1`, jigsaw `v1.8.8`, metalsmith `2.7.0`, gatsby `5.16.1`, astro `7.3.5`, @11ty/eleventy `3.1.6`, hexo `8.1.2`, next `16.3.8`, vitepress `1.6.4`.
- `-cs` values and meaning (KB per post): `0.500`=1 paragraph, `500`=1000, `1000`=2000, `5000`=10000, `10000`=20000, `100000`=200000 paragraphs. Default `0.500`.

## Review Focus

1. **Unknown / legacy `-cs` value** — `[500]` from old scripts or `0.500` must keep their meaning; an unknown value must fail loudly, not silently fall back to one paragraph. Pinned by `test_cs_rejects_unknown` in Task 3 (the shell-side counterpart `test_content_size_unknown_fails` is Task 1 of `ssg-frameworks` `docs/specs/001-canonical-build-runner/tasks.md`).

---

### Task 1: Workspace and dev tooling

**Files:**
- Create: `requirements-dev.txt`, `pyproject.toml`, `tests/__init__.py`, `tests/conftest.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `.venv` with deps; `tests/conftest.py::fake_benchmarker(tmp_path)` fixture returning an object with `.config` (attributes listed below) and `.results`-free; used by Tasks 2–3 of this file and by Task 1 of `docs/specs/002-hyperfine-results/tasks.md`.

- [ ] **Step 1: Create the SF worktree inside BT** (already done 2026-10-04; verify with `ls frameworks`)

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

(The `frameworks/` worktree shows as modified submodule content in `git status`; never `git add frameworks` until `docs/specs/003-benchmark-round-2026/tasks.md` Task 1.)

### Task 2: Python 3 port of the toolset

**Files:**
- Modify: `toolset/benchmark/test_types/__init__.py`, `toolset/utils/metadata.py`, `toolset/utils/scaffolding.py`, `toolset/utils/output_helper.py`, `toolset/utils/docker_helper.py`, `toolset/utils/results.py` (only `__parse_stats` `next()` calls and deletion of unused `__calculate_average_stats`), any other file `compileall`/ruff flags
- Test: `tests/test_imports.py`, `tests/test_metadata.py`

**Interfaces:**
- Consumes: `fake_benchmarker` fixture (Task 1).
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
6. `toolset/utils/results.py`: delete the unused `__calculate_average_stats` method (it is never called and indexes `dict.items()`). Leave `__parse_stats` for `docs/specs/002-hyperfine-results/tasks.md` Task 1.
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

### Task 3: CLI fixes (`-cs`, `-v`, help texts)

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

### Task 4: Toolset image, launcher and image names

**Files:**
- Modify: `Dockerfile`, `ssgberk`, `toolset/utils/docker_helper.py` (tags + filters), `toolset/utils/benchmark_config.py` (no change expected; verify), `toolset/utils/scaffolding.py` and `toolset/scaffolding/*` (any `matheusrv` text)
- Test: `tests/test_docker_helper.py` (create)

**Interfaces:**
- Produces: image `ssgberk/toolset`; generator images `ssgberk/test.<name>`; `DockerHelper.is_ssgberk_test_image(tag: str) -> bool` (staticmethod) used by `clean` and `__stop_all`.

- [ ] **Step 1: Failing test** — create `tests/test_docker_helper.py`:

```python
import pytest

from toolset.utils import docker_helper


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
- Produces: `changed_tests(changed_files: list[str], all_test_dirs: list[str], canonical_build_sh: str = "Go/hugo/build.sh") -> list[str]` in `toolset/github_actions/github_actions_diff.py`; CLI `python3 toolset/github_actions/github_actions_diff.py --base <ref> --repo <path>` prints one test dir (`Lang/name`) per line. Used by SF CI in `ssg-frameworks` `docs/specs/001-canonical-build-runner/tasks.md` Task 2.

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

(The end-to-end smoke job is added in `docs/specs/003-benchmark-round-2026/tasks.md` Task 1, once the submodule points at the modernized generators.)

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
- Add a section "Measurement notes" / "Notas de medição" with the three bullets from the Measurement notes in `docs/specs/001-python3-toolset/plan.md` (Risks) (bundler-dominated JS generators; Docker Desktop on macOS is for validation, publish numbers from native Linux; large `-nf` scenarios generate content slowly in bash).
- Add a "Content size" table with the `-cs` → KB mapping from Global Constraints.
- Keep the TechEmpower credit sentence.

- [ ] **Step 4: Run** — `.venv/bin/pytest -q && .venv/bin/ruff check toolset tests && grep -rn "matheusrv\|travis" README.md package.json toolset ssgberk Dockerfile deployment` → tests pass; grep prints nothing.

- [ ] **Step 5: Commit** — `git add -A .github toolset deployment README.md package.json .travis.yml && git commit -m "ci: replace travis with github actions; refresh vagrant and docs" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`
