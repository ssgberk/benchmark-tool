import types

import pytest
from unittest import mock

from toolset.benchmark import noise


def test_no_rerun_below_threshold():
    assert not noise.needs_rerun({"cv": 0.10}, 5)
    assert not noise.needs_rerun({"cv": 0.05}, 5)
    assert not noise.needs_rerun({"cv": None}, 5)


def test_no_rerun_single_run():
    assert not noise.needs_rerun({"cv": 0.5}, 2)
    assert not noise.needs_rerun({"cv": 0.5}, 1)
    assert noise.needs_rerun({"cv": 0.5}, 3)


def test_rerun_runs_capped():
    assert noise.rerun_runs(5) == 10
    assert noise.rerun_runs(8) == 10
    assert noise.rerun_runs(3) == 6


def test_rerun_reports_last_attempt():
    a1 = {"cv": 0.15, "median": 1.0}
    a2 = {"cv": 0.12, "median": 2.0}
    r = noise.finalize([a1, a2], 0.10)
    assert r["median"] == 2.0 and r["noisy"] is True
    assert [a["cv"] for a in r["attempts"]] == [0.15, 0.12]
    assert "runs" not in r["attempts"][0] and "minRuns" in r["attempts"][0]
    a2 = {"cv": 0.04, "median": 2.0}
    r = noise.finalize([a1, a2], 0.10)
    assert r["median"] == 2.0 and r["noisy"] is False


def test_finalize_single_attempt_not_noisy():
    r = noise.finalize([{"cv": 0.01, "minRuns": 5}], 0.10)
    assert r["noisy"] is False and len(r["attempts"]) == 1


def test_finalize_below_three_runs_has_no_noisy_key():
    r = noise.finalize([{"cv": None, "minRuns": 1}], 0.10)
    assert "noisy" not in r


def _bm(tmp_path, cvs, min_runs="5", statuses=None):
    from toolset.benchmark.benchmarker import Benchmarker
    b = Benchmarker.__new__(Benchmarker)
    b.config = types.SimpleNamespace(
        min_runs=min_runs, run_test_timeout_seconds=10, resources={"cpus": 1})
    test_type = mock.Mock()
    test_type.get_script_name.return_value = "build.sh"
    test_type.get_script_variables.return_value = {"min_runs": min_runs}
    b.config.types = {"datarate": test_type}
    raw = tmp_path / "raw.txt"
    b.results = mock.Mock()
    b.results.get_raw_file.return_value = str(raw)
    it = iter(cvs)
    calls = []

    def bench(ft, script, variables, raw_file, res, timeout):
        calls.append(dict(variables))
        with open(raw_file, "w") as f:
            f.write("attempt%d" % len(calls))
        return {"status": (statuses or ["ok"] * 9)[len(calls) - 1], "exitCode": 0}

    def parse(ft, tt):
        return {"results": [{"cv": next(it), "median": len(calls)}], "status": "ok",
                "failureReason": None, "unsupported": False}

    b.docker_helper = mock.Mock()
    b.docker_helper.benchmark.side_effect = bench
    b.results.parse_test.side_effect = parse
    b._Benchmarker__begin_logging = mock.Mock()
    b._Benchmarker__end_logging = mock.Mock()
    ft = mock.Mock()
    ft.name = "gen"
    ft.runTests = {"datarate": mock.Mock(failed=False)}
    return b, ft, calls


def test_benchmarker_reruns_once(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.2, 0.3, 0.9])
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert [c["min_runs"] for c in calls] == ["5", 10]
    assert b.config.types["datarate"].get_script_variables()["min_runs"] == "5"
    reported = b.results.report_benchmark_results.call_args[0][2][0]
    assert reported["noisy"] is True and len(reported["attempts"]) == 2
    assert [a["minRuns"] for a in reported["attempts"]] == [5, 10]
    assert reported["minRuns"] == "10"
    assert (tmp_path / "raw.attempt1.txt").read_text() == "attempt1"
    assert (tmp_path / "raw.txt").read_text() == "attempt2"


def test_benchmarker_no_rerun_when_quiet(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.02])
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 1
    reported = b.results.report_benchmark_results.call_args[0][2][0]
    assert reported["noisy"] is False


def _args(b):
    return b.results.report_benchmark_results.call_args[0]


@pytest.mark.parametrize("status", ["timeout", "oom"])
def test_benchmarker_no_rerun_on_nonok_first_attempt(tmp_path, status):
    b, ft, calls = _bm(tmp_path, [0.5], statuses=[status])
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 1
    assert _args(b)[2] == [] and _args(b)[4] == status


def test_benchmarker_no_rerun_when_first_attempt_failed_to_parse(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.5])
    b.results.parse_test.side_effect = None
    b.results.parse_test.return_value = {
        "results": [], "status": "failed", "failureReason": "build failed",
        "unsupported": False}
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 1 and _args(b)[2] == []


def test_failed_rerun_is_reported_as_failure(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.5, 0.5], statuses=["ok", "timeout"])
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 2
    assert _args(b)[2] == [] and _args(b)[4] == "timeout"
    assert (tmp_path / "raw.attempt1.txt").read_text() == "attempt1"
    assert (tmp_path / "raw.txt").read_text() == "attempt2"


def test_below_three_runs_no_rerun_and_no_noisy_key(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.9], min_runs="1")
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 1
    assert "noisy" not in _args(b)[2][0]


def test_cooldown_sleep_called_between_tests():
    from toolset.benchmark.benchmarker import Benchmarker
    for cooldown, expected in ((15, 2), (0, 0)):
        b = Benchmarker.__new__(Benchmarker)
        b.config = types.SimpleNamespace(
            mode="benchmark", run_id="r", allow_concurrent=True, cpus=4.0,
            memory=1, cpuset="auto", resources={"cpus": 1}, cooldown_seconds=cooldown,
            quiet_out=mock.MagicMock())
        b.metadata = mock.Mock()
        b.tests = [mock.Mock(), mock.Mock(), mock.Mock()]
        b.results = mock.Mock()
        b.results.directory = "/tmp"
        b.docker_helper = mock.Mock()
        b._Benchmarker__run_test = mock.Mock(return_value=True)
        with mock.patch("toolset.benchmark.benchmarker.time.sleep") as sleep, \
                mock.patch("builtins.open", mock.mock_open()):
            b.run()
        assert sleep.call_count == expected
        if expected:
            sleep.assert_called_with(15)


@pytest.mark.parametrize("status", ["timeout", "oom"])
def test_benchmark_returns_false_on_timeout_or_oom(tmp_path, status):
    b, ft, _ = _bm(tmp_path, [0.01], statuses=[status])
    assert b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w")) is False


@pytest.mark.parametrize("status,reason", [("failed", "SSGBERK_VERIFY_FAIL x"),
                                           ("nonconformant", "nonconformant: y"),
                                           ("failed", None)])
def test_benchmark_returns_false_on_failed_build(tmp_path, status, reason):
    b, ft, _ = _bm(tmp_path, [0.01])
    b.results.parse_test.side_effect = None
    b.results.parse_test.return_value = {
        "results": [], "status": status, "failureReason": reason, "unsupported": False}
    assert b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w")) is False


def test_benchmark_returns_true_on_ok_and_unsupported(tmp_path):
    b, ft, _ = _bm(tmp_path, [0.01])
    assert b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w")) is True
    b, ft, _ = _bm(tmp_path, [0.01])
    b.results.parse_test.side_effect = None
    b.results.parse_test.return_value = {
        "results": [], "status": "unsupported", "failureReason": None, "unsupported": True}
    assert b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w")) is True


@pytest.mark.parametrize("ok,expected", [(True, False), (False, True)])
def test_run_reports_failed_benchmark(tmp_path, ok, expected):
    from toolset.benchmark.benchmarker import Benchmarker
    b = Benchmarker.__new__(Benchmarker)
    b.config = types.SimpleNamespace(
        mode="benchmark", run_id="r", allow_concurrent=True, resources={"cpus": 1},
        cooldown_seconds=0, exclude=None, quiet_out=mock.MagicMock())
    b.metadata = mock.Mock()
    b.time_logger = mock.Mock()
    b.results = mock.Mock()
    b.results.directory = str(tmp_path)
    b.docker_helper = mock.Mock()
    test = mock.Mock()
    test.name = "gen"
    b.tests = [test]
    b._Benchmarker__benchmark = mock.Mock(return_value=ok)
    assert b.run() is expected
