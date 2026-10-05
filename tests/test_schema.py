import re
import json
import pathlib
import shutil
import types

from toolset.utils import merge_results, summary
from toolset.utils.results import Results

from tests.test_environment import FakeDocker, RES, _load

FIX = pathlib.Path(__file__).parent / "fixtures"
V1 = FIX / "results_v1.json"

TOP_TYPES = {
    "schemaVersion": int, "suite": dict, "profile": str, "resources": dict,
    "protocol": dict, "environment": dict, "generators": dict, "imageBuild": dict,
    "unsupported": dict, "failureReasons": dict,
}
RESULT_TYPES = {
    "user": float, "system": float, "cpuUtilization": float, "memoryUsageBytes": list,
    "peakRssBytes": int, "inputFiles": int, "inputBytes": int, "outputFiles": int,
    "outputBytes": int, "cv": float, "postsPerSecond": float, "inputMBPerSecond": float,
    "status": str, "features": list, "resources": dict, "conformance": str,
}


def _full_results(fake_benchmarker, tmp_path):
    cfg = fake_benchmarker.config
    cfg.resources = dict(RES)
    cfg.cooldown_seconds = 15
    cfg.suite_info = {"name": "standard", "version": 1, "cellIndex": 3, "cellCount": 5,
                      "runs": 5, "ranked": True}
    fake_benchmarker.docker_helper = types.SimpleNamespace(
        server=FakeDocker(_load("docker_info.json"), _load("docker_version.json")))
    fake_benchmarker.tests = [types.SimpleNamespace(
        name="hugo", runTests=["datarate"],
        image_build={"seconds": 41.8, "imageId": "sha256:x", "sizeBytes": 1, "noCache": False})]
    res = Results(fake_benchmarker)
    pathlib.Path(res.get_raw_file("hugo", "datarate")).write_text(
        (FIX / "raw_v2_ok.txt").read_text())
    res.parse_all(fake_benchmarker.tests[0])
    return res


def test_v2_top_level_keys(fake_benchmarker, tmp_path):
    out = _full_results(fake_benchmarker, tmp_path)._Results__to_jsonable()
    assert out["schemaVersion"] == 2
    for key, typ in TOP_TYPES.items():
        assert isinstance(out[key], typ), key
    assert set(out["suite"]) == {"name", "version", "cellIndex", "cellCount", "runs", "ranked"}
    assert {"coldRebuild", "warmupBuilds", "sequential", "concurrent", "cooldownSeconds",
            "timeoutSeconds", "cvThreshold"} <= set(out["protocol"])
    assert re.fullmatch(r"[0-9a-f]{12}", out["environment"]["fingerprint"])
    [r] = out["rawData"]["datarate"]["hugo"]
    for key, typ in RESULT_TYPES.items():
        assert isinstance(r[key], typ), key
    assert r["resources"] == out["resources"]


def test_v2_ad_hoc_run_has_null_suite_and_environment(fake_benchmarker):
    out = Results(fake_benchmarker)._Results__to_jsonable()
    assert out["schemaVersion"] == 2
    assert out["suite"] is None and out["environment"] is None


def _v1():
    return json.loads(V1.read_text())


def test_v1_fixture_is_pre_008():
    v1 = _v1()
    assert "schemaVersion" not in v1 and "environment" not in v1 and "suite" not in v1


def test_v1_results_still_parse(fake_benchmarker, tmp_path):
    cfg = fake_benchmarker.config
    cfg.number_of_files, cfg.content_size, cfg.min_runs = "100", "0.500", "3"
    res = Results(fake_benchmarker)
    v1 = _v1()
    pathlib.Path(res.file).write_text(json.dumps(v1))
    res.load()
    assert res.uuid == v1["uuid"] and res.startTime == v1["startTime"]
    for name in ("hugo", "zola"):
        shutil.copy(FIX / "v1_raw" / name / "datarate" / "raw.txt",
                    res.get_raw_file(name, "datarate"))
        res.parse_all(types.SimpleNamespace(name=name, runTests=["datarate"]))
        new = res.rawData["datarate"][name][0]
        old = v1["rawData"]["datarate"][name][0]
        for key, value in old.items():
            assert new[key] == value and type(new[key]) is type(value), (name, key)
    assert set(res.succeeded["datarate"]) >= {"hugo", "zola"}


def test_old_keys_unchanged(fake_benchmarker):
    v1 = _v1()
    cfg = fake_benchmarker.config
    res = Results(fake_benchmarker)
    pathlib.Path(res.file).write_text(json.dumps(v1))
    res.load()
    out = res._Results__to_jsonable()
    assert set(v1) - {"environments", "name"} <= set(out)
    for key in ("uuid", "startTime", "completionTime", "frameworks", "duration", "completed",
                "succeeded", "failed", "git", "environmentDescription"):
        assert out[key] == v1[key] and type(out[key]) is type(v1[key]), key
    assert out["rawData"]["datarate"] == v1["rawData"]["datarate"]
    assert cfg is not None


def test_summary_reads_v1():
    v1 = _v1()
    rows = summary.build_rows(v1, {})
    assert len(rows) == len(v1["frameworks"])
    assert summary.to_csv(rows) and summary.to_markdown(rows, v1)


def test_merge_reads_v1(tmp_path):
    v1 = _v1()
    merged = merge_results.merge([v1])
    assert set(v1) <= set(merged)
    assert sorted(merged["rawData"]["datarate"]) == sorted(v1["rawData"]["datarate"])
    assert "schemaVersion" not in merged
    p = tmp_path / "in" / "results.json"
    p.parent.mkdir()
    p.write_text(json.dumps(v1))
    assert merge_results.main(["--out", str(tmp_path / "out"), str(p)]) == 0
