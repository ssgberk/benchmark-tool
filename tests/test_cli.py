import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "run_tests", pathlib.Path(__file__).parent.parent / "toolset" / "run-tests.py")
run_tests = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_tests)


def parse(*argv):
    return run_tests.build_parser().parse_args(list(argv))


def test_cs_default_is_half_kb():
    assert parse().content_size == "0.500"


def test_cs_accepts_100000_as_single_value():
    assert parse("-cs", "100000").content_size == "100000"


def test_cs_rejects_unknown():
    with pytest.raises(SystemExit):
        parse("-cs", "7")


def test_verbose_is_flag():
    assert parse("-v").verbose is True
    assert parse().verbose is False


def test_help_texts_are_specific():
    helps = {a.dest: a.help for a in run_tests.build_parser()._actions}
    assert "number of" in helps["number_of_files"].lower()
    assert "kb" in helps["content_size"].lower()
    assert "runs" in helps["min_runs"].lower()


def test_type_rejects_update():
    with pytest.raises(SystemExit):
        parse("--type", "update")
    assert parse("--type", "datarate").type == ["datarate"]


def _patched_main(monkeypatch, **cfg):
    import types
    from unittest import mock
    seen = {}

    def fake_config(args):
        seen["args"] = args
        ns = types.SimpleNamespace(new=False, audit=False, clean=False,
                                   list_tests=False, parse=None)
        ns.__dict__.update(cfg)
        return ns

    monkeypatch.setattr(run_tests, "BenchmarkConfig", fake_config)
    bench = mock.Mock()
    monkeypatch.setattr(run_tests, "Benchmarker", lambda config: bench)
    monkeypatch.setattr(run_tests.signal, "signal", lambda *a: None)
    return seen, bench


def test_main_honours_argv(monkeypatch):
    seen, _ = _patched_main(monkeypatch)
    run_tests.main(["run-tests.py", "--test", "hugo", "-nf", "7"])
    assert seen["args"].test == ["hugo"] and seen["args"].number_of_files == "7"


def test_parse_reparses_raw_files_and_preserves_metadata(monkeypatch, fake_benchmarker, tmp_path):
    import json
    import pathlib
    import types
    from toolset.utils.results import Results

    monkeypatch.setenv("FWROOT", str(tmp_path))
    fake_benchmarker.config.timestamp = "20260101000000"
    fake_benchmarker.config.verbose_build = False
    res = Results(fake_benchmarker)
    old = {"uuid": "old-uuid", "name": "old-name", "startTime": 111, "completionTime": 222,
           "frameworks": ["hugo", "zola"], "completed": {"hugo": "done"},
           "environmentDescription": "old-env", "git": {"commitId": "abc"},
           "rawData": {"datarate": {"stale": []}},
           "succeeded": {"datarate": ["stale"]}, "failed": {"datarate": []}}
    pathlib.Path(res.file).write_text(json.dumps(old))
    test = types.SimpleNamespace(name="hugo", runTests={"datarate": object()})
    raw = pathlib.Path(res.get_raw_file("hugo", "datarate"))
    raw.write_text((pathlib.Path(__file__).parent / "fixtures" / "raw_ok.txt").read_text(encoding="utf-8"),
                   encoding="utf-8")
    res._Results__count_commits = lambda: None
    res._Results__count_sloc = lambda: None

    seen, bench = _patched_main(monkeypatch, parse="20260101000000")
    bench.results = res
    bench.metadata.gather_tests.return_value = [test]
    assert run_tests.main(["run-tests.py", "--parse", "20260101000000"]) == 0

    data = json.loads(pathlib.Path(res.file).read_text())
    for key in ("uuid", "name", "startTime", "completionTime", "frameworks", "completed",
                "environmentDescription", "git"):
        assert data[key] == old[key], key
    assert data["rawData"]["datarate"]["hugo"][0]["mean"] == 0.12
    assert "stale" not in data["rawData"]["datarate"]
    assert data["succeeded"]["datarate"] == ["hugo"]


def test_parse_missing_directory_fails_without_creating_it(monkeypatch, tmp_path):
    monkeypatch.setenv("FWROOT", str(tmp_path))
    seen, bench = _patched_main(monkeypatch)
    assert run_tests.main(["run-tests.py", "--parse", "nope"]) == 1
    assert not (tmp_path / "results" / "nope").exists()
    assert "args" not in seen  # BenchmarkConfig never constructed


def test_parse_directory_without_raw_files_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("FWROOT", str(tmp_path))
    (tmp_path / "results" / "empty").mkdir(parents=True)
    _patched_main(monkeypatch)
    assert run_tests.main(["run-tests.py", "--parse", "empty"]) == 1


def test_main_returns_1_when_run_raises(monkeypatch):
    seen, bench = _patched_main(monkeypatch)
    bench.run.side_effect = RuntimeError("boom")
    assert run_tests.main(["run-tests.py"]) == 1
