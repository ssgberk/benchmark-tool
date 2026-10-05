import copy
import csv
import io
import json
import pathlib
import shutil

import pytest

from toolset.utils import summary
from toolset.utils.summary import BASE_COLUMNS, COLUMNS, METHOD_COLUMNS, build_rows, to_csv, to_markdown

FIX = pathlib.Path(__file__).parent / "fixtures" / "suite_standard"
CELL = FIX / "core" / "nf100-cs0.500" / "results.json"

R26 = ("suite,suiteVersion,profile,features,fingerprint,cv,noisy,attempts,user,system,"
       "cpuUtilization,peakRssMB,inputMB,outputFiles,outputMB,postsPerSecond,"
       "inputMBPerSecond,imageBuildSeconds,failureReason").split(",")


def _cell():
    return json.loads(CELL.read_text())


def _csv(rows):
    return list(csv.DictReader(io.StringIO(to_csv(rows))))


def test_csv_columns_order():
    header = to_csv(build_rows(_cell(), {})).splitlines()[0].split(",")
    assert header == BASE_COLUMNS + R26 == COLUMNS
    assert METHOD_COLUMNS == R26


def test_methodology_values():
    rows = _csv(build_rows(_cell(), {}))
    hugo = next(r for r in rows if r["framework"] == "hugo")
    assert hugo["suite"] == "standard" and hugo["suiteVersion"] == "1"
    assert hugo["profile"] == "core" and hugo["fingerprint"] == "3f9c1a7b20de"
    assert hugo["noisy"] == "false" and hugo["attempts"] == "1"
    assert hugo["peakRssMB"] == "300.0" and hugo["imageBuildSeconds"] == "40.0"


def test_status_values():
    res = _cell()
    for name in ("hugo", "eleventy", "gatsby"):
        res["rawData"]["datarate"].pop(name)
    res["frameworks"] = ["hugo", "eleventy", "gatsby", "jekyll"]
    res["unsupported"] = {"datarate": ["jekyll"]}
    res["failureReasons"] = {"hugo": "timeout", "eleventy": "oom",
                             "gatsby": "nonconformant: SSGBERK_CONFORMANCE_FAIL x"}
    rows = {r["framework"]: r for r in _csv(build_rows(res, {}))}
    assert {k: v["status"] for k, v in rows.items()} == {
        "hugo": "timeout", "eleventy": "oom", "gatsby": "nonconformant", "jekyll": "unsupported"}
    for r in rows.values():
        assert all(r[c] == "" for c in ("mean", "median", "cv", "peakRssMB", "postsPerSecond"))
    assert rows["gatsby"]["failureReason"].startswith("nonconformant")


def test_ranking_never_mixes_groups():
    a = build_rows(_cell(), {})
    other = _cell()
    other["environment"]["fingerprint"] = "ffffffffffff"
    b = build_rows(other, {})
    md = to_markdown(a + b, _cell())
    assert md.count("### ") == 2
    assert "fingerprint 3f9c1a7b20de" in md and "fingerprint ffffffffffff" in md


def test_missing_environment_is_not_ranked():
    res = _cell()
    res["environment"] = None
    rows = build_rows(res, {})
    assert all(r["rank"] == "" for r in rows)
    assert "not ranked: no environment fingerprint" in to_markdown(rows, res)


def test_concurrent_not_ranked():
    res = _cell()
    res["protocol"]["concurrent"] = True
    md = to_markdown(build_rows(res, {}), res)
    assert "not ranked: concurrent run" in md


def test_ranked_labels_and_overlap():
    rows = build_rows(_cell(), {})
    assert [r["rank"] for r in rows] == ["1", "2", "3"]
    res = _cell()
    for fw in res["rawData"]["datarate"].values():
        fw[0].update(min=0.5, max=99.0)
    assert [r["rank"] for r in build_rows(res, {})] == ["=1", "=1", "=1"]


def test_legacy_not_ranked():
    res = _cell()
    res.pop("schemaVersion")
    rows = build_rows(res, {})
    assert all(r["rank"] == "" for r in rows)
    md = to_markdown(rows, res)
    assert "not ranked: legacy" in md and "### " not in md
    res2 = _cell()
    res2["suite"]["ranked"] = False
    assert all(r["rank"] == "" for r in build_rows(res2, {}))


def test_caveat_block_docker_desktop():
    res = _cell()
    assert "T1:" not in to_markdown(build_rows(res, {}), res)
    res["environment"]["docker"]["operatingSystem"] = "Docker Desktop"
    md = to_markdown(build_rows(res, {}), res)
    assert "T1: Docker Desktop runs the generators in a Linux VM" in md


def test_noisy_marker():
    res = _cell()
    res["rawData"]["datarate"]["hugo"][0]["noisy"] = True
    md = to_markdown(build_rows(res, {}), res)
    assert "hugo ⚠" in md and "eleventy ⚠" not in md
    assert "Noisy:" in md


def test_null_cv_and_v1_results_summarize():
    res = _cell()
    res["rawData"]["datarate"]["hugo"][0].update(cv=None, noisy=None)
    to_markdown(build_rows(res, {}), res)
    v1 = json.loads((pathlib.Path(__file__).parent / "fixtures" / "results_v1.json").read_text())
    rows = build_rows(v1, {})
    assert rows and all(r["rank"] == "" for r in rows)
    to_markdown(rows, v1)


def test_suite_summary_files_written(tmp_path):
    out = tmp_path / "run"
    shutil.copytree(FIX, out)
    summary.write_suite_summary(str(out), {"hugo": "Go"})
    rows = list(csv.DictReader((out / "suite-summary.csv").open()))
    assert len(rows) == 15 and list(rows[0].keys()) == ["cell"] + COLUMNS
    scaling = list(csv.DictReader((out / "scaling.csv").open()))
    assert list(scaling[0].keys()) == ["framework", "profile", "contentSize",
                                       "numberOfFiles", "median"]
    # cs 0.500 has 3 cells (100, 1000, 10000), cs 500 has 2: both listed (>= 2 cells)
    assert len(scaling) == 3 * (3 + 2)
    md = (out / "suite-summary.md").read_text()
    assert "Scaling exponent" in md
    hugo = [ln for ln in md.splitlines() if ln.startswith("| hugo | core | 0.500")]
    assert hugo and hugo[0].rstrip(" |").split("|")[-1].strip() not in ("—", "")
    two = [ln for ln in md.splitlines() if ln.startswith("| hugo | core | 500")]
    assert two and two[0].rstrip(" |").endswith("—")


def test_suite_summary_aborted_and_missing_cells(tmp_path):
    out = tmp_path / "run"
    shutil.copytree(FIX, out)
    shutil.rmtree(out / "core" / "nf10000-cs0.500")
    doc = json.loads((out / "suite.json").read_text())
    doc["aborted"] = "RuntimeError: boom"
    (out / "suite.json").write_text(json.dumps(doc))
    summary.write_suite_summary(str(out))
    md = (out / "suite-summary.md").read_text()
    assert "ABORTED: RuntimeError: boom" in md and "4 of 5" in md


def _runner_input(name, fp):
    res = _cell()
    for other in list(res["rawData"]["datarate"]):
        if other != name:
            res["rawData"]["datarate"].pop(other)
    res["frameworks"] = [name]
    res["succeeded"] = {"datarate": [name]}
    res["environment"]["fingerprint"] = fp
    return res


def test_merged_rounds_group_by_runner_fingerprint():
    from toolset.utils.merge_results import merge
    merged = merge([_runner_input("hugo", "aaa"), _runner_input("gatsby", "bbb")])
    assert merged["fingerprints"] == {"hugo": "aaa", "gatsby": "bbb"}
    rows = build_rows(merged, {})
    assert all(r["rank"] == "1" for r in rows)
    md = to_markdown(rows, merged)
    assert md.count("### ") == 2
    same = merge([_runner_input("hugo", "aaa"), _runner_input("gatsby", "aaa")])
    rows = build_rows(same, {})
    assert sorted(r["rank"] for r in rows) == ["1", "2"]
    assert to_markdown(rows, same).count("### ") == 1
    none = merge([_runner_input("hugo", None), _runner_input("gatsby", "aaa")])
    ranks = {r["framework"]: r["rank"] for r in build_rows(none, {})}
    assert ranks == {"hugo": "", "gatsby": "1"}


def test_suite_summary_cell_column_and_failure_rows(tmp_path):
    out = tmp_path / "run"
    shutil.copytree(FIX, out)
    path = out / "core" / "nf1000-cs500" / "results.json"
    res = json.loads(path.read_text())
    res["rawData"]["datarate"].pop("gatsby")
    res["failureReasons"] = {"gatsby": "timeout"}
    path.write_text(json.dumps(res))
    summary.write_suite_summary(str(out))
    rows = list(csv.DictReader((out / "suite-summary.csv").open()))
    assert list(rows[0].keys()) == ["cell"] + COLUMNS
    bad = [r for r in rows if r["status"] == "timeout"]
    assert len(bad) == 1
    assert bad[0]["cell"] == "nf1000-cs500" and bad[0]["numberOfFiles"] == "1000"
    assert bad[0]["contentSize"] == "500" and bad[0]["median"] == ""


def test_merge_results_suite_csv_same_layout(tmp_path):
    from toolset.utils import merge_results
    rows = [dict(r, cell="nf100-cs0.500") for r in build_rows(_cell(), {})]
    merge_results.write_suite_summary(rows, str(tmp_path))
    text = (tmp_path / "suite-summary.csv").read_text()
    assert text == summary.suite_csv(rows)
    assert text.splitlines()[0].split(",")[:2] == ["cell", "framework"]


def test_suite_summary_zero_cells(tmp_path):
    (tmp_path / "suite.json").write_text(json.dumps(
        {"suite": "standard", "version": 1, "cells": [], "aborted": "x"}))
    summary.write_suite_summary(str(tmp_path))
    assert (tmp_path / "scaling.csv").exists() and (tmp_path / "suite-summary.csv").exists()


def test_caveat_wording():
    res = _cell()
    res["rawData"]["datarate"]["hugo"][0]["noisy"] = True
    res["protocol"]["cvThreshold"] = 0.2
    res["protocol"]["concurrent"] = True
    md = to_markdown(build_rows(res, {}), res)
    assert "above 20%" in md and "may be affected" in md
