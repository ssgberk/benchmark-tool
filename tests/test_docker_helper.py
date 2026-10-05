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


def test_benchmarker_resolves_resources_once_and_reports_oom(monkeypatch, tmp_path):
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
