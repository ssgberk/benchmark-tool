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
        "nonconformant", "SSGBERK_CONFORMANCE_FAIL profile=core missing=title")
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


def test_transition_tolerates_missing_conformance():
    text = "\n".join(l for l in _v2().splitlines() if "CONFORMANCE" not in l)
    assert classify_build_output(text) == ("ok", None)
    [r] = parse_build_output(text, "1000", "0.500", "3")
    assert r["features"] is None


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
        "gatsby": "SSGBERK_CONFORMANCE_FAIL profile=core missing=title"}
