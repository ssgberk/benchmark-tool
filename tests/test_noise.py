import types
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
    a2 = {"cv": 0.04, "median": 2.0}
    r = noise.finalize([a1, a2], 0.10)
    assert r["median"] == 2.0 and r["noisy"] is False


def test_finalize_single_attempt_not_noisy():
    r = noise.finalize([{"cv": 0.01}], 0.10)
    assert r["noisy"] is False and len(r["attempts"]) == 1


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
    assert (tmp_path / "raw.attempt1.txt").read_text() == "attempt1"
    assert (tmp_path / "raw.txt").read_text() == "attempt2"


def test_benchmarker_no_rerun_when_quiet(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.02])
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 1
    reported = b.results.report_benchmark_results.call_args[0][2][0]
    assert reported["noisy"] is False


def test_benchmarker_no_rerun_on_timeout(tmp_path):
    b, ft, calls = _bm(tmp_path, [0.5], statuses=["timeout"])
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert len(calls) == 1


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
