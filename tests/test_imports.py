import importlib

import pytest

MODULES = [
    "toolset.benchmark.benchmarker",
    "toolset.benchmark.framework_test",
    "toolset.benchmark.test_types",
    "toolset.utils.audit",
    "toolset.utils.benchmark_config",
    "toolset.utils.cleaner",
    "toolset.utils.docker_helper",
    "toolset.utils.metadata",
    "toolset.utils.output_helper",
    "toolset.utils.results",
    "toolset.utils.scaffolding",
    "toolset.utils.time_logger",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name):
    importlib.import_module(name)
