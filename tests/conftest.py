import types

import pytest


@pytest.fixture
def fake_config(tmp_path):
    cfg = types.SimpleNamespace(
        fw_root=str(tmp_path),
        lang_root=str(tmp_path / "frameworks"),
        results_root=str(tmp_path / "results"),
        timestamp="20261004000000",
        results_name="test-run",
        results_environment="pytest",
        results_upload_uri=None,
        number_of_files="10",
        content_size="0.500",
        min_runs="1",
        profile="core",
        verbose_build=False,
        duration=15,
        test=None,
        test_dir=None,
        test_lang=None,
        exclude=None,
        types={},
    )
    (tmp_path / "frameworks").mkdir()
    return cfg


@pytest.fixture
def fake_benchmarker(fake_config):
    return types.SimpleNamespace(config=fake_config, tests=[])
