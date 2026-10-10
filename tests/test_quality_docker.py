import io
import json
import tarfile
import types
from unittest import mock

import docker
import pytest

from toolset.utils import docker_helper

RES = {"cpus": 4.0, "memoryBytes": 8589934592, "swap": False, "cpuset": "4-7"}


def _helper():
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.server = mock.Mock()
    return helper


def _container(exit_code=0, oom=False):
    c = mock.Mock()
    c.logs.return_value = iter(())
    c.wait.return_value = {"StatusCode": exit_code}
    c.attrs = {"State": {"OOMKilled": oom, "ExitCode": exit_code},
               "Config": {"WorkingDir": "/opt/hugo/src"}}
    c.get_archive.return_value = (iter([b"tar", b"bytes"]), {})
    return c


def test_benchmark_exports_output_on_success(tmp_path):
    helper, c = _helper(), _container()
    helper.server.containers.run.return_value = c
    dest = tmp_path / "quality" / "hugo" / "site.tar"
    out = helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"),
                           RES, 60, export=("public", str(dest)))
    assert out["status"] == "ok"
    c.get_archive.assert_called_once_with("/opt/hugo/src/public")
    assert dest.read_bytes() == b"tarbytes"
    c.remove.assert_called_once_with(force=True)


@pytest.mark.parametrize("exit_code,oom", [(1, False), (137, True)])
def test_benchmark_no_export_on_failure(tmp_path, exit_code, oom):
    helper, c = _helper(), _container(exit_code, oom)
    helper.server.containers.run.return_value = c
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"),
                     RES, 60, export=("public", str(tmp_path / "site.tar")))
    c.get_archive.assert_not_called()


def test_benchmark_export_error_keeps_status(tmp_path):
    helper, c = _helper(), _container()
    c.get_archive.side_effect = docker.errors.NotFound("no such path")
    helper.server.containers.run.return_value = c
    out = helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"),
                           RES, 60, export=("public", str(tmp_path / "site.tar")))
    assert out == {"status": "ok", "exitCode": 0}


def test_benchmark_without_export_never_reads_archive(tmp_path):
    helper, c = _helper(), _container()
    helper.server.containers.run.return_value = c
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"), RES, 60)
    c.get_archive.assert_not_called()


def _raw_tar(payload):
    buf = io.BytesIO()
    data = json.dumps(payload).encode()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo("raw.json")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_run_quality_isolated_and_cleaned_up(tmp_path):
    helper = _helper()
    helper._quality_image = "sha256:q"
    c = mock.Mock()
    c.wait.return_value = {"StatusCode": 0}
    c.logs.return_value = b""
    c.get_archive.return_value = (iter([_raw_tar({"tools": {"node": "v24"}})]), {})
    helper.server.containers.create.return_value = c
    tar_path = tmp_path / "site.tar"
    tar_path.write_bytes(b"site-tar")
    pages = {"index": {"url": "/", "file": "index.html"}}
    raw = helper.run_quality(str(tar_path), "public", pages)
    assert raw == {"tools": {"node": "v24"}}
    args, kwargs = helper.server.containers.create.call_args
    assert args[0] == "sha256:q"
    assert kwargs["network_mode"] == "none"
    assert "volumes" not in kwargs and "mounts" not in kwargs
    assert kwargs["command"][:4] == ["node", "/quality/run.mjs", "--site", "/work/public"]
    assert json.loads(kwargs["command"][kwargs["command"].index("--pages") + 1]) == pages
    c.put_archive.assert_called_once_with("/work", b"site-tar")
    c.get_archive.assert_called_once_with("/quality-out/raw.json")
    c.remove.assert_called_once_with(force=True)


def test_run_quality_out_dir_never_inside_site(tmp_path):
    helper = _helper()
    helper._quality_image = "sha256:q"
    c = mock.Mock()
    c.wait.return_value = {"StatusCode": 0}
    c.get_archive.return_value = (iter([_raw_tar({})]), {})
    helper.server.containers.create.return_value = c
    (tmp_path / "site.tar").write_bytes(b"x")
    helper.run_quality(str(tmp_path / "site.tar"), "out", {})
    command = helper.server.containers.create.call_args[1]["command"]
    site = command[command.index("--site") + 1]
    out = command[command.index("--out") + 1]
    assert site == "/work/out"
    assert out != site and not out.startswith(site + "/")
    assert out == docker_helper.QUALITY_OUT and not out.startswith("/work")


def test_run_quality_without_raw_json_raises_and_cleans_up(tmp_path):
    helper = _helper()
    helper._quality_image = "sha256:q"
    c = mock.Mock()
    c.wait.return_value = {"StatusCode": 1}
    c.logs.return_value = b"Error: boom"
    c.get_archive.side_effect = docker.errors.NotFound("missing")
    helper.server.containers.create.return_value = c
    (tmp_path / "site.tar").write_bytes(b"x")
    with pytest.raises(RuntimeError, match="exit 1.*boom"):
        helper.run_quality(str(tmp_path / "site.tar"), "public", {})
    c.remove.assert_called_once_with(force=True)


def test_build_quality_image_once(monkeypatch, tmp_path):
    builds = []

    class FakeAPIClient:
        def __init__(self, base_url=None):
            pass

        def build(self, **kw):
            builds.append(kw)
            return iter([{"stream": "Step 1/2 : FROM ubuntu:24.04\n"}, {"stream": "Successfully built abc\n"}])

    monkeypatch.setattr(docker_helper.docker, "APIClient", FakeAPIClient)
    helper = _helper()
    helper._quality_image = None
    helper.benchmarker.config = types.SimpleNamespace(fw_root=str(tmp_path), server_docker_host=None)
    helper.server.images.get.return_value = types.SimpleNamespace(id="sha256:abc")
    assert helper.build_quality_image() == "sha256:abc"
    assert helper.build_quality_image() == "sha256:abc"
    assert len(builds) == 1
    assert builds[0]["path"] == str(tmp_path / "quality") and builds[0]["tag"] == docker_helper.QUALITY_IMAGE


def test_build_quality_image_error(monkeypatch, tmp_path):
    class FakeAPIClient:
        def __init__(self, base_url=None):
            pass

        def build(self, **kw):
            return iter([{"errorDetail": {"message": "npm ci failed"}}])

    monkeypatch.setattr(docker_helper.docker, "APIClient", FakeAPIClient)
    helper = _helper()
    helper._quality_image = None
    helper.benchmarker.config = types.SimpleNamespace(fw_root=str(tmp_path), server_docker_host=None)
    with pytest.raises(RuntimeError, match="npm ci failed"):
        helper.build_quality_image()
