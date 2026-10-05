import pathlib

from toolset.utils.results import Results, classify_build_output, parse_build_output

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


def test_parse_stats_skips_repeated_header_block(fake_benchmarker):
    # dool appends to an existing file, so a noise re-run adds a second header
    # block; parsing must skip it and keep the rows of the reported attempt.
    fake_benchmarker.tests = []
    res = Results(fake_benchmarker)
    stats_file = res.get_stats_file("hugo", "datarate")
    csv_text = (FIX / "dool.csv").read_text()
    pathlib.Path(stats_file).write_text(csv_text + csv_text)
    stats = res._Results__parse_stats(type("T", (), {"name": "hugo"})(), "datarate", 0, 10**10, 1)
    assert stats, "expected sampled rows"
    assert all(isinstance(t, float) for t in stats)


def _fw(name):
    return type("T", (), {"name": name, "runTests": ["datarate"]})()


def test_unsupported_recorded_not_failed(fake_benchmarker):
    fake_benchmarker.tests = []
    res = Results(fake_benchmarker)
    fw = _fw("hugo")
    raw = res.get_raw_file("hugo", "datarate")
    pathlib.Path(raw).write_text("SSGBERK_PROFILE_UNSUPPORTED extended\n")
    res.parse_all(fw)
    assert res.unsupported["datarate"] == ["hugo"]
    assert "hugo" not in res.failed["datarate"]
    assert "hugo" not in res.succeeded["datarate"]
    out = res._Results__to_jsonable()
    assert out["unsupported"] == {"datarate": ["hugo"]}
    assert out["profile"] == "core"


def test_failed_still_failed_and_profile_recorded(fake_benchmarker):
    fake_benchmarker.config.profile = "extended"
    res = Results(fake_benchmarker)
    pathlib.Path(res.get_raw_file("x", "datarate")).write_text("nothing\n")
    res.parse_all(_fw("x"))
    assert res.failed["datarate"] == ["x"] and res.unsupported["datarate"] == []
    assert res._Results__to_jsonable()["profile"] == "extended"


def test_unsupported_marker_with_valid_result_counts_as_succeeded(fake_benchmarker):
    fake_benchmarker.config.number_of_files = "10"
    fake_benchmarker.config.content_size = "0.500"
    fake_benchmarker.config.min_runs = "1"
    res = Results(fake_benchmarker)
    text = "SSGBERK_PROFILE_UNSUPPORTED extended\n" + (FIX / "raw_ok.txt").read_text()
    pathlib.Path(res.get_raw_file("hugo", "datarate")).write_text(text)
    res.parse_all(_fw("hugo"))
    assert res.unsupported["datarate"] == []
    assert res.failed["datarate"] == []
    assert res.succeeded["datarate"] == ["hugo"]


def test_results_json_profile_matches_cell_dir(fake_benchmarker):
    fake_benchmarker.config.profile = "extended"
    fake_benchmarker.config.timestamp = "20261004000000/extended/nf10-cs0.500"
    res = Results(fake_benchmarker)
    assert res.directory.endswith("extended/nf10-cs0.500")
    assert res._Results__to_jsonable()["profile"] == "extended"


def _v2():
    return (FIX / "raw_v2_ok.txt").read_text()


def test_v2_fields():
    [r] = parse_build_output(_v2(), "1000", "0.500", "3")
    assert r["status"] == "ok"
    assert (r["user"], r["system"]) == (3.91, 0.62)
    assert r["memoryUsageBytes"] == [512000000, 514000000, 513000000]
    assert r["peakRssBytes"] == 514000000
    assert r["cpuUtilization"] == round((3.91 + 0.62) / 2.61, 3)
    assert (r["inputFiles"], r["inputBytes"]) == (1000, 512000)
    assert (r["outputFiles"], r["outputBytes"]) == (1004, 905000)
    assert r["postsPerSecond"] == 1000 / 2.5
    assert r["inputMBPerSecond"] == 512000 / 1e6 / 2.5
    assert r["cv"] == 0.0522 / 2.61
    assert r["features"] == []
    assert r["mean"] == 2.61 and r["numberOfFiles"] == "1000"


def test_features_parsed_from_conformance_ok():
    text = _v2().replace("features=-", "features=tags,rss")
    [r] = parse_build_output(text, "1000", "0.500", "3")
    assert r["features"] == ["tags", "rss"]


def test_v1_raw_still_parses():
    [r] = parse_build_output((FIX / "raw_ok.txt").read_text(), "10", "0.500", "1")
    for k in ("peakRssBytes", "memoryUsageBytes", "inputFiles", "inputBytes",
              "outputFiles", "outputBytes", "cv", "inputMBPerSecond",
              "features"):
        assert r[k] is None, k
    assert r["status"] == "ok"
    assert r["postsPerSecond"] == 10 / 0.12  # derivable from nf and median
    assert (r["user"], r["system"]) == (0.1, 0.02)
    assert r["cpuUtilization"] == 1.0
    assert r["mean"] == 0.12 and r["median"] == 0.12


def test_conformance_fail_is_failed_with_reason():
    text = (FIX / "raw_conformance_fail.txt").read_text()
    assert classify_build_output(text) == (
        "nonconformant", "nonconformant: SSGBERK_CONFORMANCE_FAIL profile=core missing=title")
    assert parse_build_output(text + _v2(), "1", "1", "1") == []


def test_verify_fail_classified():
    text = "SSGBERK_VERIFY_FAIL expected=10 got=0\n" + _v2()
    assert classify_build_output(text) == (
        "failed", "SSGBERK_VERIFY_FAIL expected=10 got=0")


def test_unsupported_status():
    text = (FIX / "raw_unsupported.txt").read_text()
    assert classify_build_output(text) == ("unsupported", None)
    assert parse_build_output(text, "1", "1", "1") == []


def test_verify_ok_must_precede_starttime():
    reason = "protocol: verification markers missing before STARTTIME"
    late = _v2().replace("SSGBERK_VERIFY_OK expected=1000 got=1000\n", "") \
        + "SSGBERK_VERIFY_OK expected=1000 got=1000\n"
    assert classify_build_output(late) == ("failed", reason)
    assert parse_build_output(late, "1000", "0.500", "3") == []
    late_conf = _v2().replace(
        "SSGBERK_CONFORMANCE_OK profile=core posts=1000 sampled=10 features=-\n", "") \
        + "SSGBERK_CONFORMANCE_OK profile=core posts=1000 sampled=10 features=-\n"
    assert classify_build_output(late_conf) == ("failed", reason)


def _no_conf():
    return "\n".join(l for l in _v2().splitlines() if "CONFORMANCE" not in l)


def test_missing_conformance_tolerated_by_default_and_recorded():
    assert classify_build_output(_no_conf()) == ("ok", None)
    [r] = parse_build_output(_no_conf(), "1000", "0.500", "3")
    assert r["features"] is None and r["conformance"] == "unchecked"
    [r] = parse_build_output(_v2(), "1000", "0.500", "3")
    assert r["conformance"] == "ok"


def test_require_conformance_fails_missing_marker():
    assert classify_build_output(_no_conf(), require_conformance=True) == (
        "nonconformant", "nonconformant: missing SSGBERK_CONFORMANCE_OK")
    assert parse_build_output(_no_conf(), "1000", "0.500", "3",
                              require_conformance=True) == []
    assert classify_build_output(_v2(), require_conformance=True) == ("ok", None)


def test_require_conformance_flows_through_config(fake_benchmarker):
    fake_benchmarker.tests = []
    fake_benchmarker.config.number_of_files = "1000"
    fake_benchmarker.config.content_size = "0.500"
    fake_benchmarker.config.min_runs = "3"
    fake_benchmarker.config.require_conformance = True
    res = Results(fake_benchmarker)
    pathlib.Path(res.get_raw_file("hugo", "datarate")).write_text(_no_conf())
    res.parse_all(_fw("hugo"))
    assert res.failed["datarate"] == ["hugo"]
    assert res._Results__to_jsonable()["failureReasons"] == {
        "hugo": "nonconformant: missing SSGBERK_CONFORMANCE_OK"}


def test_crlf_and_leading_whitespace_markers():
    text = "\r\n".join("  " + l for l in _v2().splitlines()) + "\r\n"
    [r] = parse_build_output(text, "1000", "0.500", "3")
    assert r["inputBytes"] == 512000 and r["outputFiles"] == 1004
    assert r["features"] == [] and r["conformance"] == "ok"
    assert r["startTime"] == 1790000000
    fail = "  SSGBERK_CONFORMANCE_FAIL profile=core x=1\r\n"
    assert classify_build_output(fail) == (
        "nonconformant", "nonconformant: SSGBERK_CONFORMANCE_FAIL profile=core x=1")


def test_conformance_fail_after_starttime():
    text = _v2() + "SSGBERK_CONFORMANCE_FAIL late\n"
    assert classify_build_output(text)[0] == "nonconformant"
    assert parse_build_output(text, "1000", "0.500", "3") == []


def test_missing_io_markers_give_none_metrics():
    text = "\n".join(l for l in _v2().splitlines()
                     if not l.startswith(("SSGBERK_INPUT", "SSGBERK_OUTPUT")))
    [r] = parse_build_output(text, "1000", "0.500", "3")
    for k in ("inputFiles", "inputBytes", "outputFiles", "outputBytes",
              "inputMBPerSecond"):
        assert r[k] is None, k
    assert r["peakRssBytes"] == 514000000


def test_memory_usage_scalar_and_absent():
    scalar = _v2().replace('[512000000, 514000000, 513000000]', '512000000')
    [r] = parse_build_output(scalar, "1000", "0.500", "3")
    assert r["memoryUsageBytes"] == [512000000] and r["peakRssBytes"] == 512000000
    absent = "\n".join(l for l in _v2().splitlines() if "memory_usage_byte" not in l)
    [r] = parse_build_output(absent, "1000", "0.500", "3")
    assert r["memoryUsageBytes"] is None and r["peakRssBytes"] is None


def test_cv_null_for_single_run():
    [r] = parse_build_output((FIX / "raw_ok.txt").read_text(), "10", "0.500", "1")
    assert r["cv"] is None


def test_failure_reason_stored_and_emitted(fake_benchmarker):
    fake_benchmarker.tests = []
    res = Results(fake_benchmarker)
    res.config.number_of_files = "10"
    res.config.content_size = "0.500"
    res.config.min_runs = "1"
    raw = res.get_raw_file("gatsby", "datarate")
    pathlib.Path(raw).write_text((FIX / "raw_conformance_fail.txt").read_text())
    res.parse_all(_fw("gatsby"))
    assert res.failed["datarate"] == ["gatsby"]
    out = res._Results__to_jsonable()
    assert out["failureReasons"] == {
        "gatsby": "nonconformant: SSGBERK_CONFORMANCE_FAIL profile=core missing=title"}


def test_every_result_carries_identical_resources(fake_benchmarker):
    fake_benchmarker.tests = []
    fake_benchmarker.config.resources = {"cpus": 4.0, "memoryBytes": 1, "swap": False,
                                         "cpuset": "4-7"}
    res = Results(fake_benchmarker)
    res.report_benchmark_results(_fw("a"), "datarate", [{"mean": 1.0}])
    res.report_benchmark_results(_fw("b"), "datarate", [{"mean": 2.0}])
    out = res._Results__to_jsonable()
    assert out["rawData"]["datarate"]["a"][0]["resources"] == out["resources"]
    assert out["rawData"]["datarate"]["b"][0]["resources"] == out["resources"]


def test_results_json_has_environment_and_generators(fake_benchmarker):
    import json as _json, os as _os
    from types import SimpleNamespace
    fw = _os.path.join(fake_benchmarker.config.fw_root, "frameworks")
    with open(_os.path.join(fw, "generators.json"), "w") as f:
        _json.dump({"generators": [{"id": "hugo", "version": "0.167.0"}]}, f)
    fake_benchmarker.config.resources = {"cpus": 4.0, "memoryBytes": 1, "swap": False, "cpuset": None}
    fake_benchmarker.tests = [SimpleNamespace(name="hugo")]
    fake_benchmarker.docker_helper = SimpleNamespace(server=SimpleNamespace(
        info=lambda: {"NCPU": 8}, version=lambda: {"Version": "29"},
        images=SimpleNamespace(get=lambda n: (_ for _ in ()).throw(Exception("x")))))
    out = Results(fake_benchmarker)._Results__to_jsonable()
    assert out["environment"]["docker"]["ncpu"] == 8
    assert len(out["environment"]["fingerprint"]) == 12
    assert out["generators"]["hugo"]["version"] == "0.167.0"
    assert out["generators"]["hugo"]["imageId"] is None


def test_results_json_environment_null_without_docker(fake_benchmarker):
    out = Results(fake_benchmarker)._Results__to_jsonable()
    assert out["environment"] is None


def test_image_build_in_results_not_in_rawdata(fake_benchmarker):
    from types import SimpleNamespace
    ib = {"seconds": 41.8, "imageId": "sha256:a", "sizeBytes": 1, "noCache": False}
    fake_benchmarker.tests = [SimpleNamespace(name="hugo", image_build=ib),
                              SimpleNamespace(name="zola")]
    res = Results(fake_benchmarker)
    res.report_benchmark_results(SimpleNamespace(name="hugo"), "datarate", [{"mean": 2.0}])
    out = res._Results__to_jsonable()
    assert out["imageBuild"] == {"hugo": ib}
    row = out["rawData"]["datarate"]["hugo"][0]
    assert "imageBuild" not in row and "seconds" not in row
    assert row["mean"] == 2.0


PENDING = "SSGBERK_CONFORMANCE_PENDING nav-missing aria-current not found\n"


def _pending():
    # SF 006 R-3 report mode: PENDING, no OK, then timing follows
    return _no_conf().replace("SSGBERK_OUTPUT", PENDING + "SSGBERK_OUTPUT", 1)


def test_conformance_pending_tolerated_when_switch_off():
    assert classify_build_output(_pending()) == ("ok", None)
    [r] = parse_build_output(_pending(), "1000", "0.500", "3")
    assert r["conformance"] == "unchecked" and r["median"] == 2.5


def test_conformance_pending_nonconformant_when_required():
    assert classify_build_output(_pending(), require_conformance=True) == (
        "nonconformant", "nonconformant: " + PENDING.strip())
    assert parse_build_output(_pending(), "1000", "0.500", "3",
                              require_conformance=True) == []


def test_unknown_conformance_marker_still_protocol_failure():
    text = _no_conf().replace("STARTTIME", "SSGBERK_CONFORMANCE_BOGUS\nSTARTTIME", 1)
    assert classify_build_output(text) == (
        "failed", "protocol: verification markers missing before STARTTIME")
