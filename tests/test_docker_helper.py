import types
from unittest import mock

import pytest

from toolset.utils import docker_helper


@pytest.mark.parametrize("tag,expected", [
    ("ssgberk/test.hugo:latest", True),
    ("ssgberk/toolset:latest", False),
    ("matheusrv/ssgberk.test.hugo:latest", False),
    ("nginx:latest", False),
])
def test_is_ssgberk_test_image(tag, expected):
    assert docker_helper.DockerHelper.is_ssgberk_test_image(tag) is expected


RES = {"cpus": 4.0, "memoryBytes": 8589934592, "swap": False, "cpuset": "4-7"}


def _ok_container(chunks=()):
    c = mock.Mock()
    c.logs.return_value = iter(chunks)
    c.wait.return_value = {"StatusCode": 0}
    c.attrs = {"State": {"OOMKilled": False, "ExitCode": 0}}
    return c


def test_benchmark_writes_raw_chunks_verbatim(tmp_path):
    chunks = [b'SSGBERK_RESULT_BEGIN\n{"results":[{"mean":12.', b'34}]}\nSSGBERK_RESULT_END\n']
    container = _ok_container(chunks)
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.server = mock.Mock()
    helper.server.containers.run.return_value = container
    raw = tmp_path / "raw.txt"
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(raw), RES, 60)
    assert '"mean":12.34}' in raw.read_text()


class _FakeTimeLogger:
    def mark_build_start(self):
        pass

    def time_since_start(self):
        return 0

    def log_build_end(self, log_prefix=None, file=None):
        pass


def _build_with_tokens(monkeypatch, tokens, log_file):
    class FakeAPIClient:
        def __init__(self, base_url=None):
            pass

        def build(self, **kw):
            return iter(tokens)

    monkeypatch.setattr(docker_helper.docker, "APIClient", FakeAPIClient)
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = types.SimpleNamespace(time_logger=_FakeTimeLogger())
    helper._DockerHelper__build("unix://x", ".", str(log_file), "pfx", "a.dockerfile", "tag")


def test_build_writes_stream_tokens_to_log(monkeypatch, tmp_path):
    log_file = tmp_path / "build.log"
    _build_with_tokens(monkeypatch, [{'stream': 'Step 1/2 : FROM x\n'}, {'stream': 'done\n'}], log_file)
    text = log_file.read_text()
    assert "Step 1/2 : FROM x" in text
    assert "done" in text


def test_build_raises_on_error_detail(monkeypatch, tmp_path):
    with pytest.raises(Exception):
        _build_with_tokens(monkeypatch, [{'errorDetail': {'message': 'boom'}}], tmp_path / "build.log")


import docker.errors  # noqa: E402


def _helper(run_id="abc12345-0000"):
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.benchmarker.config.run_id = run_id
    helper.benchmarker.config.network = "ssgberk"
    helper.benchmarker.config.network_mode = None
    helper.benchmarker.config.mode = "benchmark"
    helper.server = mock.Mock()
    return helper


def test_run_labels_and_unique_name(tmp_path):
    helper = _helper()
    with mock.patch.object(docker_helper, "Thread"):
        helper.run(types.SimpleNamespace(name="hugo"), str(tmp_path))
    kw = helper.server.containers.run.call_args.kwargs
    assert kw["labels"] == {"ssgberk.run": "abc12345-0000"}
    assert kw["name"] == "ssgberk-abc12345-hugo"


def test_benchmark_labels():
    helper = _helper()
    helper.server.containers.run.return_value = _ok_container()
    helper.benchmark(types.SimpleNamespace(name="hugo"), "b.sh", {}, "/dev/null", RES, 60)
    kw = helper.server.containers.run.call_args.kwargs
    assert kw["labels"] == {"ssgberk.run": "abc12345-0000"}


def test_stop_all_scoped_to_run_label(monkeypatch):
    monkeypatch.setattr(docker_helper.time, "sleep", lambda s: None)
    helper = _helper()
    mine = mock.Mock()
    helper.server.containers.list.return_value = [mine]
    helper.stop()
    helper.server.containers.list.assert_called_once_with(
        filters={"label": "ssgberk.run=abc12345-0000"})
    mine.stop.assert_called_once()


def test_stop_all_tolerates_not_found(monkeypatch):
    monkeypatch.setattr(docker_helper.time, "sleep", lambda s: None)
    helper = _helper()
    gone = mock.Mock()
    gone.stop.side_effect = docker.errors.NotFound("gone")
    ok = mock.Mock()
    helper.server.containers.list.return_value = [gone, ok]
    helper.stop()
    ok.stop.assert_called_once()
    helper.server.containers.list.side_effect = docker.errors.ImageNotFound("x")
    helper.stop()  # must not raise
    helper.server.containers.list.side_effect = docker.errors.NotFound("x")
    helper.stop()


def test_benchmark_decodes_multibyte_split_across_chunks(tmp_path):
    encoded = "Time (abs ≡): 0.1 s\n".encode("utf-8")
    cut = encoded.index("≡".encode("utf-8")) + 1  # split inside the 3-byte char
    container = _ok_container([encoded[:cut], encoded[cut:]])
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.server = mock.Mock()
    helper.server.containers.run.return_value = container
    raw = tmp_path / "raw.txt"
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(raw), RES, 60)
    text = raw.read_text(encoding="utf-8")
    assert "≡" in text and "�" not in text


def _bench(helper, tmp_path):
    return helper.benchmark(types.SimpleNamespace(name="hugo"), "b.sh", {},
                            str(tmp_path / "raw.txt"), RES, 60)


def test_benchmark_passes_resource_limits(tmp_path):
    helper = _helper()
    helper.server.containers.run.return_value = _ok_container()
    out = _bench(helper, tmp_path)
    kw = helper.server.containers.run.call_args.kwargs
    assert kw["nano_cpus"] == 4_000_000_000
    assert kw["mem_limit"] == kw["memswap_limit"] == 8589934592
    assert kw["cpuset_cpus"] == "4-7"
    assert kw["remove"] is False and kw["detach"] is True
    assert out == {"status": "ok", "exitCode": 0}


def test_benchmark_no_cpuset_passes_none(tmp_path):
    helper = _helper()
    helper.server.containers.run.return_value = _ok_container()
    helper.benchmark(types.SimpleNamespace(name="hugo"), "b.sh", {}, str(tmp_path / "r"),
                     dict(RES, cpuset=None), 60)
    assert helper.server.containers.run.call_args.kwargs["cpuset_cpus"] is None


def test_benchmark_timeout(tmp_path):
    import requests
    helper = _helper()
    c = _ok_container()
    c.wait.side_effect = requests.exceptions.ReadTimeout("t")
    c.attrs = {"State": {"OOMKilled": False, "ExitCode": 137}}
    helper.server.containers.run.return_value = c
    out = _bench(helper, tmp_path)
    assert out["status"] == "timeout"
    c.wait.assert_called_once_with(timeout=60)
    c.stop.assert_called_once()
    c.remove.assert_called_once_with(force=True)


def test_benchmark_oom(tmp_path):
    helper = _helper()
    c = _ok_container()
    c.wait.return_value = {"StatusCode": 137}
    c.attrs = {"State": {"OOMKilled": True, "ExitCode": 137}}
    helper.server.containers.run.return_value = c
    assert _bench(helper, tmp_path) == {"status": "oom", "exitCode": 137}
    c.remove.assert_called_once_with(force=True)


def test_container_removed_after_inspect(tmp_path):
    helper = _helper()
    c = _ok_container()
    parent = mock.Mock()
    parent.attach_mock(c.reload, "reload")
    parent.attach_mock(c.remove, "remove")
    helper.server.containers.run.return_value = c
    _bench(helper, tmp_path)
    names = [call[0] for call in parent.mock_calls]
    assert names == ["reload", "remove"]


def test_benchmark_removes_container_on_error(tmp_path):
    helper = _helper()
    c = _ok_container()
    c.wait.side_effect = RuntimeError("boom")
    helper.server.containers.run.return_value = c
    with pytest.raises(RuntimeError):
        _bench(helper, tmp_path)
    c.remove.assert_called_once_with(force=True)


def test_benchmarker_resolves_resources_once_and_caches_on_config(monkeypatch, tmp_path):
    from toolset.benchmark.benchmarker import Benchmarker
    b = Benchmarker.__new__(Benchmarker)
    b.config = types.SimpleNamespace(cpus=4.0, memory=8589934592, cpuset="auto",
                                     resources=None)
    b.docker_helper = mock.Mock()
    b.docker_helper.server.info.return_value = {"NCPU": 8}
    assert b.resolve_resources()["cpuset"] == "4-7"
    b.resolve_resources()
    b.docker_helper.server.info.assert_called_once()
    assert b.config.resources["swap"] is False


def test_benchmark_exit_137_without_oomkilled_flag_is_oom(tmp_path):
    helper = _helper()
    c = _ok_container()
    c.wait.return_value = {"StatusCode": 137}
    c.attrs = {"State": {"OOMKilled": False, "ExitCode": 137}}
    helper.server.containers.run.return_value = c
    assert _bench(helper, tmp_path) == {"status": "oom", "exitCode": 137}


def test_benchmark_timeout_stopped_137_stays_timeout(tmp_path):
    import requests
    helper = _helper()
    c = _ok_container()
    c.wait.side_effect = requests.exceptions.ReadTimeout("t")
    c.attrs = {"State": {"OOMKilled": False, "ExitCode": 137}}
    helper.server.containers.run.return_value = c
    assert _bench(helper, tmp_path)["status"] == "timeout"


def test_connect_timeout_is_not_a_generator_timeout(tmp_path):
    import requests
    helper = _helper()
    c = _ok_container()
    c.wait.side_effect = requests.exceptions.ConnectTimeout("Connection to x timed out")
    helper.server.containers.run.return_value = c
    with pytest.raises(requests.exceptions.ConnectTimeout):
        _bench(helper, tmp_path)
    c.stop.assert_not_called()
    c.remove.assert_called_once_with(force=True)


def _bm(**cfg):
    from toolset.benchmark.benchmarker import Benchmarker
    b = Benchmarker.__new__(Benchmarker)
    base = dict(mode="benchmark", run_id="r", allow_concurrent=True, cpus=4.0,
                memory=8589934592, cpuset="auto", resources=None,
                quiet_out=mock.MagicMock())
    base.update(cfg)
    b.config = types.SimpleNamespace(**base)
    b.metadata = mock.Mock()
    b.tests = [mock.Mock()]
    b.results = mock.Mock()
    b.docker_helper = mock.Mock()
    b.docker_helper.server.info.return_value = {"NCPU": 8}
    b.docker_helper.other_runs.return_value = []
    b._Benchmarker__run_test = mock.Mock(return_value=False)
    return b


def test_run_rejects_too_many_cpus_before_any_test(tmp_path):
    b = _bm(cpus=16.0)
    b.results.directory = str(tmp_path)
    with mock.patch("toolset.benchmark.benchmarker.log") as log:
        with pytest.raises(SystemExit) as exc:
            b.run()
    assert exc.value.code == 1
    assert any("exceeds" in str(c) for c in log.call_args_list)
    b._Benchmarker__run_test.assert_not_called()
    b.docker_helper.benchmark.assert_not_called()


def test_run_resolves_resources_into_config_before_tests(tmp_path):
    b = _bm()
    b.results.directory = str(tmp_path)
    seen = []
    b._Benchmarker__run_test.side_effect = lambda *a: seen.append(b.config.resources) or False
    b.run()
    assert seen[0]["cpuset"] == "4-7"


@pytest.mark.parametrize("status", ["oom", "timeout"])
def test_benchmark_status_routes_to_failed_with_reason(fake_benchmarker, tmp_path, status):
    import pathlib
    from toolset.benchmark.benchmarker import Benchmarker
    from toolset.utils.results import Results
    fake_benchmarker.tests = []
    res = Results(fake_benchmarker)
    b = Benchmarker.__new__(Benchmarker)
    b.config = fake_benchmarker.config
    b.config.resources = dict(RES)
    b.config.run_test_timeout_seconds = 60
    b.config.types = {"datarate": mock.Mock()}
    b.results = res
    b.docker_helper = mock.Mock()
    b.docker_helper.benchmark.return_value = {"status": status, "exitCode": 137}
    b._Benchmarker__begin_logging = mock.Mock()
    b._Benchmarker__end_logging = mock.Mock()
    fw = types.SimpleNamespace(
        name="gatsby", runTests={"datarate": types.SimpleNamespace(failed=False)})
    # whatever the generator printed before dying must not count as a result
    raw = pathlib.Path(res.get_raw_file("gatsby", "datarate"))
    raw.write_text("SSGBERK_PROFILE_UNSUPPORTED extended\n")
    b._Benchmarker__benchmark(fw, mock.MagicMock())
    assert "gatsby" in res.failed["datarate"]
    assert "gatsby" not in res.unsupported["datarate"]
    assert res._Results__to_jsonable()["failureReasons"]["gatsby"] == status
    assert "gatsby" not in res.rawData["datarate"]


def _build_helper(images_get=None):
    helper = _helper()
    helper.benchmarker.config.no_cache = False
    helper.benchmarker.config.server_docker_host = "unix://x"
    helper.benchmarker.config.results_environment = "e"
    if images_get is not None:
        helper.server.images.get = images_get
    return helper


def test_build_records_seconds(monkeypatch):
    helper = _build_helper(lambda tag: types.SimpleNamespace(id="sha256:a", attrs={"Size": 7}))
    monkeypatch.setattr(helper, "_DockerHelper__build", lambda **kw: None)
    ticks = iter([10.0, 52.5])
    monkeypatch.setattr(docker_helper.time, "monotonic", lambda: next(ticks))
    test = types.SimpleNamespace(name="hugo", directory=".")
    assert helper.build(test) == 0
    assert helper.last_build == {"seconds": 42.5, "imageId": "sha256:a",
                                 "sizeBytes": 7, "noCache": False}


def test_build_records_seconds_on_failure_and_missing_image(monkeypatch):
    def missing(tag):
        raise docker.errors.ImageNotFound("x")
    helper = _build_helper(missing)

    def boom(**kw):
        raise Exception("x")
    monkeypatch.setattr(helper, "_DockerHelper__build", boom)
    assert helper.build(types.SimpleNamespace(name="hugo", directory=".")) == 1
    assert helper.last_build["imageId"] is None
    assert helper.last_build["sizeBytes"] is None
    assert helper.last_build["seconds"] >= 0


def test_no_cache_flag_passed(monkeypatch):
    helper = _build_helper(lambda tag: types.SimpleNamespace(id="i", attrs={}))
    helper.benchmarker.config.no_cache = True
    seen = {}
    monkeypatch.setattr(helper, "_DockerHelper__build", lambda **kw: seen.update(kw))
    helper.build(types.SimpleNamespace(name="hugo", directory="."))
    assert seen["nocache"] is True
    assert helper.last_build["noCache"] is True


def test_no_cache_reaches_docker_api(monkeypatch, tmp_path):
    seen = {}

    class FakeAPIClient:
        def __init__(self, base_url=None):
            pass

        def build(self, **kw):
            seen.update(kw)
            return iter([])
    monkeypatch.setattr(docker_helper.docker, "APIClient", FakeAPIClient)
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = types.SimpleNamespace(time_logger=_FakeTimeLogger())
    helper._DockerHelper__build("unix://x", ".", str(tmp_path / "l"), "p", "a.dockerfile", "t", nocache=True)
    assert seen["nocache"] is True


def test_failed_build_has_no_stale_image_id(monkeypatch):
    helper = _build_helper(lambda tag: types.SimpleNamespace(id="sha256:old", attrs={"Size": 9}))

    def boom(**kw):
        raise Exception("x")
    monkeypatch.setattr(helper, "_DockerHelper__build", boom)
    assert helper.build(types.SimpleNamespace(name="hugo", directory=".")) == 1
    assert helper.last_build["imageId"] is None
    assert helper.last_build["sizeBytes"] is None
    assert helper.last_build["seconds"] >= 0
