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
