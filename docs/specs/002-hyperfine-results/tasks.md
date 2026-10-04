# Hyperfine Results Contract (toolset side) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the measured build time reach `results.json`: parse the marker-delimited hyperfine JSON printed by each generator's `build.sh`, write container output verbatim to `raw.txt`, and switch resource stats from `dstat` to `dool`.

**Architecture:** `Results.parse_test` extracts the JSON between `SSGBERK_RESULT_BEGIN`/`SSGBERK_RESULT_END` (contract owned by `ssg-frameworks/docs/specs/001-canonical-build-runner`), `DockerHelper.benchmark` writes the stream byte-for-byte, `__parse_stats` reads real `dool` CSV.

**Tech Stack:** Python 3.12, pytest, ruff, dool 1.3.8, hyperfine 1.20.0 (produced by the generators).

**Spec:** `docs/specs/002-hyperfine-results/spec.md` and `docs/specs/002-hyperfine-results/plan.md` (same directory, repo `ssgberk/benchmark-tool`). Read both before starting any task.

In this file **BT** = `/Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize` (repo `ssgberk/benchmark-tool`, branch `chore/modernize-2026`) and **SF** = `BT/frameworks` (repo `ssgberk/ssg-frameworks`, branch `chore/modernize-2026`). Layout: `docs/specs/ROADMAP.md` in BT.

Prerequisite: `docs/specs/001-python3-toolset` is complete (provides `.venv`, `tests/conftest.py`, `tests/test_docker_helper.py`, the Python 3 port).

## Global Constraints

- Git author/committer `Matheus Breguêz <matbrgz@gmail.com>`; every commit GPG-signed (repo config already has `commit.gpgsign=true`, key `B6FA8458D5176E83`). Never use `--no-gpg-sign` or `--author`.
- Every commit message ends with the trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Never commit to `master`. Never push, open PRs, or close dependabot branches unless the human explicitly asks.
- Result markers printed by `build.sh`, consumed by `Results.parse_test`: `SSGBERK_RESULT_BEGIN`, `SSGBERK_RESULT_END`, `SSGBERK_VERIFY_FAIL`, `STARTTIME <epoch>`, `ENDTIME <epoch>`.

(Marker contract owned by `ssg-frameworks/docs/specs/001-canonical-build-runner`; the values above are repeated here because the tests use them.)

## Review Focus

1. **Chunked docker log stream corrupting the JSON** — `container.logs(stream=True)` yields arbitrary byte chunks; if `raw.txt` is written through `log()` (which appends a newline per chunk) a number like `12.34` can be split into `12.` / `34` and parsing silently fails, sending every generator to `failed`. Pinned by `test_benchmark_writes_raw_chunks_verbatim` in Task 1.

---

### Task 1: Results contract (hyperfine JSON, raw output, dool stats)

**Files:**
- Modify: `toolset/utils/results.py` (`parse_test`, `__parse_stats`, new module-level `parse_build_output`), `toolset/utils/docker_helper.py` (`benchmark`), `toolset/benchmark/benchmarker.py` (`__begin_logging`: `dstat` → `dool`)
- Create: `tests/fixtures/raw_ok.txt`, `tests/fixtures/dool.csv`
- Test: `tests/test_results.py`, `tests/test_docker_helper.py` (append; the file is created by `docs/specs/001-python3-toolset/tasks.md` Task 4)

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

Append to `tests/test_docker_helper.py` (created by `docs/specs/001-python3-toolset/tasks.md` Task 4; add `import types` and `from unittest import mock` at the top if missing):

```python
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
