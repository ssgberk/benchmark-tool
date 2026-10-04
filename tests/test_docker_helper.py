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


def test_benchmark_writes_raw_chunks_verbatim(tmp_path):
    chunks = [b'SSGBERK_RESULT_BEGIN\n{"results":[{"mean":12.', b'34}]}\nSSGBERK_RESULT_END\n']
    container = mock.Mock()
    container.logs.return_value = iter(chunks)
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.server = mock.Mock()
    helper.server.containers.run.return_value = container
    raw = tmp_path / "raw.txt"
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(raw))
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
