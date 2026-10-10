import json
import pathlib
import tarfile
import types
from unittest import mock

from toolset.quality import runner
from toolset.utils.results import STORED_RUN_KEYS, Results

FIX = pathlib.Path(__file__).parent / "fixtures" / "quality"


def _cfg(**kw):
    return types.SimpleNamespace(**kw)


def test_eligible_and_skipped():
    assert not runner.eligible(_cfg())
    assert not runner.skipped(_cfg())
    assert runner.eligible(_cfg(quality=True, suite_info=None, number_of_files="10", content_size="0.500"))
    p0 = _cfg(quality=True, suite_info={"name": "P"}, number_of_files="50", content_size="5")
    p1 = _cfg(quality=True, suite_info={"name": "P"}, number_of_files="50", content_size="50")
    assert runner.eligible(p0) and not runner.skipped(p0)
    assert not runner.eligible(p1) and runner.skipped(p1)


def _generator(tmp_path):
    d = tmp_path / "frameworks" / "Go" / "hugo"
    d.mkdir(parents=True)
    (d / "benchmark_config.json").write_text(json.dumps(
        {"framework": "hugo", "config": [{"output_folder": "public", "output_glob": "post/*/index.html"}]}))
    return types.SimpleNamespace(name="hugo", directory=str(d))


def _archive(results_dir):
    tar_path = pathlib.Path(runner.archive_path(str(results_dir), "hugo"))
    tar_path.parent.mkdir(parents=True)
    with tarfile.open(tar_path, "w") as tar:
        tar.add(FIX / "site", arcname="public")
    return tar_path


def test_run_pass_ok(tmp_path):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    tar_path = _archive(results_dir)
    helper = mock.Mock()
    helper.run_quality.return_value = json.loads((FIX / "raw.json").read_text())
    q = runner.run_pass(helper, test, str(results_dir))
    assert q["status"] == "ok" and q["lighthouse"]["status"] == "ok"
    args = helper.run_quality.call_args[0]
    assert args[0] == str(tar_path) and args[1] == "public"
    assert args[2]["post"] == {"url": "/post/hello/", "file": "post/hello/index.html"}
    out = results_dir / "quality" / "hugo"
    assert json.loads((out / "quality.json").read_text()) == q
    assert (out / "raw.json").exists() and (out / "site" / "index.html").exists()
    assert not tar_path.exists()


def test_run_pass_missing_archive(tmp_path):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    q = runner.run_pass(mock.Mock(), test, str(results_dir))
    assert q["status"] == "error" and "no exported output" in q["error"]
    assert json.loads((results_dir / "quality" / "hugo" / "quality.json").read_text()) == q


def test_run_pass_collector_error(tmp_path):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    _archive(results_dir)
    helper = mock.Mock()
    helper.run_quality.side_effect = RuntimeError("collector wrote no raw.json (exit 1)")
    q = runner.run_pass(helper, test, str(results_dir))
    assert q == {"status": "error", "error": "RuntimeError: collector wrote no raw.json (exit 1)"}


def _bm(tmp_path, quality=True, results=None, failure=None):
    from toolset.benchmark.benchmarker import Benchmarker
    tmp_path.mkdir(parents=True, exist_ok=True)
    b = Benchmarker.__new__(Benchmarker)
    b.config = types.SimpleNamespace(min_runs="1", run_test_timeout_seconds=10, resources={"cpus": 1},
                                     quality=quality, suite_info=None, number_of_files="50",
                                     content_size="5")
    test_type = mock.Mock()
    test_type.get_script_name.return_value = "build.sh"
    test_type.get_script_variables.return_value = {"min_runs": "1"}
    b.config.types = {"datarate": test_type}
    b.results = mock.Mock()
    b.results.directory = str(tmp_path / "results")
    b.results.get_raw_file.return_value = str(tmp_path / "raw.txt")
    exports = []

    def bench(ft, script, variables, raw_file, res, timeout, export=None):
        exports.append(export)
        return {"status": "ok", "exitCode": 0}

    b.docker_helper = mock.Mock()
    b.docker_helper.benchmark.side_effect = bench
    b.docker_helper._quality_image = "sha256:q"
    b.results.parse_test.return_value = {
        "results": [{"cv": None, "median": 1.0}] if results is None else results,
        "status": "ok", "failureReason": failure, "unsupported": False}
    b._Benchmarker__begin_logging = mock.Mock()
    b._Benchmarker__end_logging = mock.Mock()
    ft = _generator(tmp_path)
    ft.runTests = {"datarate": mock.Mock(failed=False)}
    return b, ft, exports


def test_quality_pass_runs_after_ok(tmp_path, monkeypatch):
    b, ft, exports = _bm(tmp_path)
    monkeypatch.setattr(runner, "run_pass", lambda helper, test, d: {"status": "ok", "test": test.name})
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert exports == [("public", runner.archive_path(b.results.directory, "hugo"))]
    b.results.add_quality.assert_called_once_with("hugo", {"status": "ok", "test": "hugo"}, "sha256:q")


def test_quality_pass_missing_archive_keeps_result(tmp_path):
    reported = []
    for quality in (False, True):
        b, ft, _ = _bm(tmp_path / str(quality), quality=quality)
        b._Benchmarker__benchmark(ft, open(tmp_path / ("log%s" % quality), "w"))
        # everything but the generator object (its directory differs per run)
        reported.append(b.results.report_benchmark_results.call_args[0][1:])
        if quality:
            name, q, _image = b.results.add_quality.call_args[0]
            assert name == "hugo" and q["status"] == "error"
    assert reported[0] == reported[1]


def test_no_pass_without_results_or_with_failure(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(runner, "run_pass", lambda *a: called.append(a) or {"status": "ok"})
    for i, kw in enumerate(({"results": []}, {"failure": "nonconformant: index"})):
        b, ft, _ = _bm(tmp_path / str(i), **kw)
        b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
        b.results.add_quality.assert_not_called()
    assert called == []


def test_skipped_cell_exports_nothing(tmp_path):
    b, ft, exports = _bm(tmp_path)
    b.config.suite_info = {"name": "P"}
    b.config.content_size = "50"
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert exports == [None]
    b.results.add_quality.assert_not_called()


def test_results_add_quality(fake_benchmarker):
    res = Results(fake_benchmarker)
    res._environment = {"fingerprint": "f"}  # what environment.capture would have cached
    before = res._Results__to_jsonable()
    assert "quality" not in before and "quality" not in before["environment"]
    res.add_quality("hugo", {"status": "ok", "tools": {"lighthouse": "1.0.0"}}, "sha256:q")
    after = res._Results__to_jsonable()
    assert after["quality"] == {"hugo": {"status": "ok", "tools": {"lighthouse": "1.0.0"}}}
    assert after["rawData"] == before["rawData"] and after["succeeded"] == before["succeeded"]
    assert after["environment"] == {"fingerprint": "f",
                                    "quality": {"lighthouse": "1.0.0", "image": "sha256:q"}}


def test_reparse_keeps_quality(fake_benchmarker, monkeypatch):
    assert "quality" in STORED_RUN_KEYS
    monkeypatch.setattr(Results, "_Results__count_commits", lambda self: None)
    monkeypatch.setattr(Results, "_Results__count_sloc", lambda self: None)
    res = Results(fake_benchmarker)
    with open(res.file, "w") as f:
        json.dump({"quality": {"hugo": {"status": "ok"}}, "rawData": {"datarate": {}}}, f)
    res.reparse([])
    with open(res.file) as f:
        assert json.load(f)["quality"] == {"hugo": {"status": "ok"}}


def test_run_pass_write_failure_still_returns(tmp_path, monkeypatch):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    tar_path = _archive(results_dir)
    helper = mock.Mock()
    helper.run_quality.return_value = json.loads((FIX / "raw.json").read_text())
    real_open = open

    def fake_open(path, *a, **kw):
        if str(path).endswith("quality.json"):
            raise OSError("disk full")
        return real_open(path, *a, **kw)

    monkeypatch.setattr("builtins.open", fake_open)
    q = runner.run_pass(helper, test, str(results_dir))
    assert isinstance(q, dict) and q["status"] == "ok"
    assert not tar_path.exists()


def test_quality_failure_never_changes_build_result(tmp_path, monkeypatch):
    def boom(*a):
        raise RuntimeError("kaboom")

    outcomes = []
    for quality in (False, True):
        b, ft, _ = _bm(tmp_path / str(quality), quality=quality)
        if quality:
            monkeypatch.setattr(runner, "run_pass", boom)
        ret = b._Benchmarker__benchmark(ft, open(tmp_path / ("log%s" % quality), "w"))
        outcomes.append((ret, b.results.report_benchmark_results.call_args[0][1:]))
        if quality:
            name, q, image = b.results.add_quality.call_args[0]
            assert name == "hugo" and q == {"status": "error", "error": "RuntimeError: kaboom"}
            assert image is None
    assert outcomes[0] == outcomes[1]


def test_unused_export_tar_removed(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(runner, "run_pass", lambda *a: called.append(a) or {"status": "ok"})
    for i, kw in enumerate(({"results": []}, {"failure": "nonconformant: index"})):
        b, ft, _ = _bm(tmp_path / str(i), **kw)
        tar_path = pathlib.Path(runner.archive_path(b.results.directory, "hugo"))
        tar_path.parent.mkdir(parents=True)
        tar_path.write_bytes(b"x")
        b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
        assert not tar_path.exists()
    assert called == []
