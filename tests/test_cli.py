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


def test_profile_default_core():
    assert parse().profile == "core"
    assert parse("--profile", "extended").profile == "extended"


def test_profile_rejects_unknown():
    with pytest.raises(SystemExit):
        parse("--profile", "bogus")


def test_resource_flag_defaults():
    a = parse()
    assert (a.cpus, a.memory, a.cpuset) == (4.0, 8589934592, "auto")


def test_resource_flags_parse():
    a = parse("--cpus", "2", "--memory", "512m", "--cpuset", "none")
    assert (a.cpus, a.memory, a.cpuset) == (2.0, 512 * 1024 ** 2, "none")


def test_memory_rejects_garbage():
    with pytest.raises(SystemExit):
        parse("--memory", "lots")


@pytest.mark.parametrize("failed,code", [(True, 1), (False, 0)])
def test_main_exit_code_follows_run(monkeypatch, failed, code):
    _, bench = _patched_main(monkeypatch)
    bench.run.return_value = failed
    assert run_tests.main(["run-tests.py"]) == code


def _v2_cell(tmp_path, fake_benchmarker, monkeypatch, failure=None):
    import json
    import pathlib
    import types
    from toolset.utils.results import Results

    monkeypatch.setenv("FWROOT", str(tmp_path))
    ts = "20261004000000/core/nf1000-cs0.500"
    fake_benchmarker.config.timestamp = ts
    # CLI defaults of a plain `--parse` invocation, not the cell's values
    fake_benchmarker.config.number_of_files = "10"
    fake_benchmarker.config.content_size = "0.500"
    fake_benchmarker.config.min_runs = "3"
    res = Results(fake_benchmarker)
    resources = {"cpus": 4.0, "memoryBytes": 8589934592, "swap": False, "cpuset": "4-7"}
    entry = {"mean": 9.9, "median": 9.9, "numberOfFiles": "1000", "contentSize": "0.500",
             "minRuns": "10", "noisy": True, "resources": resources,
             "attempts": [{"minRuns": 5, "cv": 0.2}, {"minRuns": 10, "cv": 0.15}]}
    old = {
        "schemaVersion": 2, "uuid": "u", "name": "n", "startTime": 1, "completionTime": 2,
        "numberOfFiles": "1000", "contentSize": "0.500", "frameworks": ["hugo", "zola"],
        "completed": {}, "environmentDescription": "e", "git": None, "duration": 15,
        "rawData": {"datarate": {"hugo": [entry]}},
        "succeeded": {"datarate": ["hugo"]}, "failed": {"datarate": ["zola"]},
        "unsupported": {"datarate": []},
        "failureReasons": {"zola": failure} if failure else {},
        "suite": {"name": "standard", "version": 1, "cellIndex": 1, "cellCount": 5,
                  "runs": 5, "ranked": True},
        "profile": "core", "resources": resources,
        "protocol": {"coldRebuild": True, "cooldownSeconds": 15, "timeoutSeconds": 7200,
                     "concurrent": False},
        "environment": {"fingerprint": "fp-1", "cpuModel": "x"},
        "generators": {"hugo": {"version": "0.1"}},
        "imageBuild": {"hugo": {"seconds": 12.5, "imageId": "sha256:a"}},
    }
    pathlib.Path(res.file).write_text(json.dumps(old))
    fixtures = pathlib.Path(__file__).parent / "fixtures"
    pathlib.Path(res.get_raw_file("hugo", "datarate")).write_text(
        (fixtures / "raw_v2_ok.txt").read_text(encoding="utf-8"), encoding="utf-8")
    pathlib.Path(res.get_raw_file("zola", "datarate")).write_text(
        "Generating 1000 posts\nkilled\n", encoding="utf-8")
    res._Results__count_commits = lambda: None
    res._Results__count_sloc = lambda: None
    tests = [types.SimpleNamespace(name=n, runTests={"datarate": object()})
             for n in ("hugo", "zola")]
    seen, bench = _patched_main(monkeypatch, parse=ts)
    bench.results = res
    bench.metadata.gather_tests.return_value = tests
    (tmp_path / "results" / ts).mkdir(parents=True, exist_ok=True)
    assert run_tests.main(["run-tests.py", "--parse", ts]) == 0
    return old, json.loads(pathlib.Path(res.file).read_text())


def test_parse_v2_cell_keeps_run_metadata_and_cell_values(monkeypatch, fake_benchmarker, tmp_path):
    old, data = _v2_cell(tmp_path, fake_benchmarker, monkeypatch)
    for key in ("suite", "profile", "resources", "protocol", "environment",
                "generators", "imageBuild", "numberOfFiles", "contentSize"):
        assert data[key] == old[key], key
    hugo = data["rawData"]["datarate"]["hugo"][0]
    assert hugo["numberOfFiles"] == "1000" and hugo["contentSize"] == "0.500"
    assert hugo["minRuns"] == "10"
    # measured fields are refreshed from raw.txt, with the cell's file count
    assert hugo["median"] == 2.5
    assert hugo["postsPerSecond"] == 1000 / 2.5
    for key in ("noisy", "attempts", "resources"):
        assert hugo[key] == old["rawData"]["datarate"]["hugo"][0][key], key
    assert data["failed"]["datarate"] == ["zola"]


def test_parse_keeps_timeout_failure_reason(monkeypatch, fake_benchmarker, tmp_path):
    _, data = _v2_cell(tmp_path, fake_benchmarker, monkeypatch, failure="timeout")
    assert data["failureReasons"]["zola"] == "timeout"
    assert "zola" in data["failed"]["datarate"]


def test_single_run_interrupt_exits_nonzero(monkeypatch):
    import signal
    handlers = {}
    _, bench = _patched_main(monkeypatch)
    monkeypatch.setattr(run_tests.signal, "signal",
                        lambda sig, handler: handlers.__setitem__(sig, handler))
    bench.stop.side_effect = SystemExit(0)  # mirrors Benchmarker.stop
    run_tests.main(["run-tests.py"])
    with pytest.raises(SystemExit) as exc:
        handlers[signal.SIGINT](signal.SIGINT, None)
    assert exc.value.code == 130
    bench.stop.assert_called_once()
    with pytest.raises(SystemExit) as exc:
        handlers[signal.SIGTERM](signal.SIGTERM, None)
    assert exc.value.code == 128 + signal.SIGTERM
