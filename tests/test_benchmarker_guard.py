import types
from unittest import mock

import docker

from toolset.benchmark.benchmarker import Benchmarker
from toolset.utils import docker_helper
from toolset.utils.results import Results


def _container(run_id):
    c = mock.Mock()
    c.labels = {"ssgberk.run": run_id}
    return c


def _helper(containers, own="own"):
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.server = mock.Mock()
    helper.server.containers.list.return_value = containers
    return helper


def _benchmarker(other_runs, directory, allow_concurrent=False):
    b = Benchmarker.__new__(Benchmarker)
    b.config = types.SimpleNamespace(mode="benchmark", run_id="own",
                                     allow_concurrent=allow_concurrent,
                                     resources={"cpus": 4.0}, cpus=4.0,
                                     quiet_out=mock.MagicMock())
    b.metadata = mock.Mock()
    b.tests = [mock.Mock()]
    b.results = mock.Mock()
    b.results.directory = str(directory)
    b.docker_helper = mock.Mock()
    b.docker_helper.other_runs.return_value = other_runs
    b._Benchmarker__run_test = mock.Mock(return_value=True)
    return b


def test_other_runs_ignores_own_run():
    helper = _helper([_container("own"), _container("other"), _container("other")])
    assert helper.other_runs("own") == ["other"]
    helper.server.containers.list.assert_called_once_with(filters={"label": "ssgberk.run"})


def test_other_runs_tolerates_not_found():
    helper = _helper([])
    helper.server.containers.list.side_effect = docker.errors.NotFound("gone")
    assert helper.other_runs("own") == []
    gone = mock.Mock()
    type(gone).labels = mock.PropertyMock(side_effect=docker.errors.NotFound("gone"))
    assert _helper([gone, _container("x")]).other_runs("own") == ["x"]


def test_guard_aborts_on_other_run(tmp_path):
    b = _benchmarker(["abc-123"], tmp_path)
    with mock.patch("toolset.benchmark.benchmarker.log") as log:
        assert b.run() is True
    b._Benchmarker__run_test.assert_not_called()
    assert any("abc-123" in str(c) for c in log.call_args_list)


def test_guard_ignores_own_run(tmp_path):
    b = _benchmarker([], tmp_path)
    b.run()
    b._Benchmarker__run_test.assert_called_once()


def test_allow_concurrent_skips_guard(tmp_path):
    b = _benchmarker(["abc-123"], tmp_path, allow_concurrent=True)
    b.run()
    b.docker_helper.other_runs.assert_not_called()
    b._Benchmarker__run_test.assert_called_once()


def test_allow_concurrent_records_flag(fake_config):
    fake_config.allow_concurrent = True
    fake_config.run_test_timeout_seconds = 900
    fake_config.cooldown_seconds = 15
    r = Results.__new__(Results)
    r.config = fake_config
    p = r._Results__protocol()
    assert p["concurrent"] is True and p["sequential"] is False
    assert p == {"coldRebuild": True, "warmupBuilds": 1, "sequential": False,
                 "concurrent": True, "cooldownSeconds": 15,
                 "timeoutSeconds": 900, "cvThreshold": 0.10}
    fake_config.allow_concurrent = False
    assert r._Results__protocol()["sequential"] is True
