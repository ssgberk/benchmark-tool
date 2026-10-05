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
    res = Results(fake_benchmarker)
    pathlib.Path(res.file).write_text(json.dumps(v1))
    res.load()
    out = res._Results__to_jsonable()
    # `environments` is a merge_results addition and `name` is regenerated per run
    # (datetime-based), so neither is compared; every other v1 key must survive.
    assert set(v1) - {"environments", "name"} <= set(out)
    for key in ("uuid", "startTime", "completionTime", "frameworks", "duration", "completed",
                "succeeded", "failed", "git", "environmentDescription"):
        assert out[key] == v1[key] and type(out[key]) is type(v1[key]), key
    assert out["rawData"]["datarate"] == v1["rawData"]["datarate"]


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


def test_noisy_and_attempts_types():
    from toolset.benchmark import noise
    r = noise.finalize([{"minRuns": 5, "mean": 2.0, "cv": 0.3}, {"minRuns": 5, "mean": 2.1, "cv": 0.2}])
    assert isinstance(r["noisy"], bool) and isinstance(r["attempts"], list)
    assert all(isinstance(a, dict) for a in r["attempts"])


def _v2(name, **extra):
    d = {"schemaVersion": 2, "frameworks": [name],
         "rawData": {"datarate": {}}, "succeeded": {"datarate": []},
         "failed": {"datarate": []}, "unsupported": {"datarate": []},
         "resources": None, "profile": "core"}
    d.update(extra)
    return d


def test_merge_combines_v2_sections():
    a = _v2("a", failureReasons={"a": "oom"}, imageBuild={"a": {"seconds": 1}},
            generators={"a": {"version": "1"}}, unsupported={"datarate": ["a"]},
            resources={"cpus": 4.0}, suite={"name": "s"})
    b = _v2("b", failureReasons={"b": "timeout"}, imageBuild={"b": {"seconds": 2}},
            generators={"b": {"version": "2"}}, unsupported={"datarate": ["b", "a"]})
    m = merge_results.merge([a, b])
    assert m["failureReasons"] == {"a": "oom", "b": "timeout"}
    assert set(m["imageBuild"]) == set(m["generators"]) == {"a", "b"}
    assert m["unsupported"] == {"datarate": ["a", "b"]}
    assert m["schemaVersion"] == 2 and m["resources"] == {"cpus": 4.0}
    assert m["suite"] == {"name": "s"}


def test_merge_schema_version_rules():
    v1 = _v1()
    assert "schemaVersion" not in merge_results.merge([v1])
    assert merge_results.merge([v1, _v2("x")])["schemaVersion"] == 2
    assert merge_results.merge([_v2("x"), v1])["schemaVersion"] == 2


def _live_entry(fake_benchmarker, raws):
    '''rawData entry produced by Benchmarker.__benchmark (the live path).'''
    from unittest import mock
    from toolset.benchmark.benchmarker import Benchmarker
    cfg = fake_benchmarker.config
    cfg.number_of_files, cfg.content_size, cfg.min_runs = "1000", "0.500", "5"
    cfg.resources = dict(RES)
    cfg.run_test_timeout_seconds = 60
    test_type = mock.Mock()
    test_type.get_script_name.return_value = "build.sh"
    test_type.get_script_variables.return_value = {"min_runs": "5"}
    cfg.types = {"datarate": test_type}
    res = Results(fake_benchmarker)
    b = Benchmarker.__new__(Benchmarker)
    b.config, b.results = cfg, res
    texts = iter(raws)

    def bench(ft, script, variables, raw_file, resources, timeout):
        pathlib.Path(raw_file).write_text(next(texts))
        return {"status": "ok", "exitCode": 0}

    b.docker_helper = mock.Mock()
    b.docker_helper.benchmark.side_effect = bench
    b._Benchmarker__begin_logging = mock.Mock()
    b._Benchmarker__end_logging = mock.Mock()
    fw = types.SimpleNamespace(name="hugo",
                               runTests={"datarate": types.SimpleNamespace(failed=False)})
    assert b._Benchmarker__benchmark(fw, mock.MagicMock()) is True
    return res._Results__to_jsonable()["rawData"]["datarate"]["hugo"][0]


def _v1_types():
    entry = next(iter(_v1()["rawData"]["datarate"].values()))[0]
    return {k: type(v) for k, v in entry.items()}


def test_live_result_keeps_v1_field_types(fake_benchmarker):
    raw = (FIX / "raw_v2_ok.txt").read_text()
    entry = _live_entry(fake_benchmarker, [raw])
    for key, typ in _v1_types().items():
        assert type(entry[key]) is typ, key
    assert entry["minRuns"] == "5"


def test_rerun_result_keeps_v1_field_types(fake_benchmarker):
    raw = (FIX / "raw_v2_ok.txt").read_text()
    noisy = raw.replace('"stddev": 0.0522', '"stddev": 0.9')
    entry = _live_entry(fake_benchmarker, [noisy, raw])
    assert len(entry["attempts"]) == 2
    for key, typ in _v1_types().items():
        assert type(entry[key]) is typ, key
    assert entry["minRuns"] == "10"
    assert [a["minRuns"] for a in entry["attempts"]] == [5, 10]
