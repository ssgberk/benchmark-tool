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
        "minRuns": "1",
        "frameworks": [name],
        "duration": 15,
        "rawData": {"datarate": {name: [{"mean": mean, "stddev": 0.0, "median": mean,
                                          "min": mean, "max": mean,
                                          "numberOfFiles": "10",
                                          "contentSize": "0.500", "minRuns": "1"}]
                                 if ok else []}},
        "completed": {},
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
