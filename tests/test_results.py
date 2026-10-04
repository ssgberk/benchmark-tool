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
