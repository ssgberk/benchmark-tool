import csv
import io
import json
import subprocess
import sys

from toolset.utils import merge_results


def _result(name, start, end, ok=True, mean=1.0):
    return {
        "uuid": "u-" + name,
        "name": "run",
        "environmentDescription": "local",
        "startTime": start,
        "completionTime": end,
        "numberOfFiles": "10",
        "contentSize": "0.500",
        "frameworks": [name],
        "duration": 15,
        "rawData": {"datarate": {name: [{"mean": mean, "stddev": 0.0, "median": mean,
                                          "min": mean, "max": mean,
                                          "numberOfFiles": "10",
                                          "contentSize": "0.500", "minRuns": "1"}]
                                 if ok else []}},
        "completed": {name: "2026-10-04 00:00:00"},
        "git": None,
        "succeeded": {"datarate": [name] if ok else []},
        "failed": {"datarate": [] if ok else [name]},
    }


def _write(tmp_path, name, data, env=None, lang=None):
    d = tmp_path / name
    d.mkdir()
    (d / "results.json").write_text(json.dumps(data))
    if env is not None:
        (d / ("env-%s.txt" % name)).write_text(env)
    if lang is not None:
        (d / "test_metadata.json").write_text(json.dumps([{"name": name, "language": lang}]))
    return str(d / "results.json")


def _two(tmp_path):
    a = _write(tmp_path, "zola", _result("zola", 2000, 3000), env="cpu A\n", lang="Rust")
    b = _write(tmp_path, "hugo", _result("hugo", 1000, 2500, ok=False), env="cpu B\n", lang="Go")
    return [a, b]


def test_merge_unions_and_sorts(tmp_path):
    merged = merge_results.merge([json.load(open(p)) for p in _two(tmp_path)])
    assert merged["frameworks"] == ["hugo", "zola"]
    assert sorted(merged["rawData"]["datarate"]) == ["hugo", "zola"]
    assert merged["succeeded"]["datarate"] == ["zola"]
    assert merged["failed"]["datarate"] == ["hugo"]
    assert "GitHub Actions ubuntu-24.04, one runner per generator" in merged["name"]
    assert merged["environmentDescription"] == \
        "GitHub Actions ubuntu-24.04, one runner per generator"


def test_merge_min_max_times(tmp_path):
    merged = merge_results.merge([json.load(open(p)) for p in _two(tmp_path)])
    assert merged["startTime"] == 1000
    assert merged["completionTime"] == 3000


def test_merge_preserves_schema_keys(tmp_path):
    src = _result("a", 1, 2)
    merged = merge_results.merge([src])
    assert set(src) <= set(merged)
    assert set(merged["rawData"]) == {"datarate"}
    assert set(merged["succeeded"]) == {"datarate"} == set(merged["failed"])


def test_main_writes_outputs_and_environments(tmp_path):
    out = tmp_path / "out"
    assert merge_results.main(["--out", str(out)] + _two(tmp_path)) == 0
    merged = json.loads((out / "results.json").read_text())
    assert merged["environments"] == {"hugo": "cpu B\n", "zola": "cpu A\n"}
    rows = list(csv.DictReader(io.StringIO((out / "summary.csv").read_text())))
    by = {r["framework"]: r for r in rows}
    assert by["zola"]["status"] == "ok" and by["zola"]["language"] == "Rust"
    assert by["hugo"]["status"] == "failed" and by["hugo"]["language"] == "Go"
    assert "| zola |" in (out / "summary.md").read_text()


def test_missing_metadata_leaves_language_empty(tmp_path):
    p = _write(tmp_path, "x", _result("x", 1, 2))
    out = tmp_path / "out"
    merge_results.main(["--out", str(out), p])
    rows = list(csv.DictReader(io.StringIO((out / "summary.csv").read_text())))
    assert rows[0]["language"] == ""


def test_cli_module(tmp_path):
    out = tmp_path / "out"
    r = subprocess.run([sys.executable, "-m", "toolset.utils.merge_results", "--out",
                        str(out)] + _two(tmp_path), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (out / "results.json").exists()


def test_completed_union_and_git_first_non_null():
    a, b, c = _result("a", 1, 2), _result("b", 1, 2), _result("c", 1, 2)
    b["git"] = {"commitId": "abc"}
    c["git"] = {"commitId": "def"}
    merged = merge_results.merge([a, b, c])
    assert set(merged["completed"]) == {"a", "b", "c"}
    assert merged["git"] == {"commitId": "abc"}


def test_duplicate_succeeded_deduplicated():
    merged = merge_results.merge([_result("a", 1, 2), _result("a", 3, 4)])
    assert merged["succeeded"]["datarate"] == ["a"]
    assert merged["frameworks"] == ["a"]


def _cell_result(name, nf, cs, mean):
    r = _result(name, 1000, 2000, mean=mean)
    r["numberOfFiles"] = nf
    r["contentSize"] = cs
    r["rawData"]["datarate"][name][0].update(numberOfFiles=nf, contentSize=cs)
    return r


def test_merge_by_cell_writes_one_summary_per_cell_and_suite_summary(tmp_path):
    paths = [
        _write(tmp_path, "a-P-0", _cell_result("a", "50", "5", 1.0)),
        _write(tmp_path, "b-P-0", _cell_result("b", "50", "5", 2.0)),
        _write(tmp_path, "a-P-1", _cell_result("a", "50", "50", 3.0)),
        _write(tmp_path, "b-P-1", _cell_result("b", "50", "50", 4.0)),
    ]
    out = tmp_path / "out"
    assert merge_results.main(["--out", str(out), "--by-cell"] + paths) == 0
    for cell in ("nf50-cs5", "nf50-cs50"):
        merged = json.loads((out / cell / "results.json").read_text())
        assert sorted(merged["rawData"]["datarate"]) == ["a", "b"]
        assert (out / cell / "summary.csv").exists()
        assert (out / cell / "summary.md").exists()
    rows = list(csv.DictReader(io.StringIO((out / "suite-summary.csv").read_text())))
    assert len(rows) == 4
    assert {r["cell"] for r in rows} == {"nf50-cs5", "nf50-cs50"}
    md = (out / "suite-summary.md").read_text()
    assert "nf50-cs5" in md and "nf50-cs50" in md


def test_by_cell_groups_same_cell_and_ignores_unrelated(tmp_path):
    paths = [_write(tmp_path, "a", _cell_result("a", "10", "0.500", 1.0))]
    out = tmp_path / "out"
    assert merge_results.main(["--out", str(out), "--by-cell"] + paths) == 0
    assert (out / "nf10-cs0.500" / "results.json").exists()
