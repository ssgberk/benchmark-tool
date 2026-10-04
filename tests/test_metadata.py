import json

from toolset.benchmark.test_types import DatarateTestType
from toolset.utils.metadata import Metadata

CONFIG = {
    "framework": "hugo",
    "tests": [{"default": {
        "approach": "Realistic", "classification": "Micro", "framework": "hugo",
        "language": "Go", "display_name": "hugo", "notes": "", "versus": "go",
    }}],
}


def test_parse_config_builds_default_test(fake_benchmarker):
    fake_benchmarker.config.types = {"datarate": DatarateTestType(fake_benchmarker.config)}
    tests = Metadata(fake_benchmarker).parse_config(CONFIG, "/x/frameworks/Go/hugo")
    assert [t.name for t in tests] == ["hugo"]
    assert list(tests[0].runTests) == ["datarate"]


def test_list_test_metadata_writes_json_list(fake_benchmarker, tmp_path):
    fake_benchmarker.config.types = {"datarate": DatarateTestType(fake_benchmarker.config)}
    d = tmp_path / "frameworks" / "Go" / "hugo"
    d.mkdir(parents=True)
    (d / "benchmark_config.json").write_text(json.dumps(CONFIG))
    fake_benchmarker.results = type("R", (), {"directory": str(tmp_path)})()
    Metadata(fake_benchmarker).list_test_metadata()
    data = json.loads((tmp_path / "test_metadata.json").read_text())
    assert isinstance(data, list) and data[0]["name"] == "hugo"


def test_gather_languages_ignores_non_directories(fake_benchmarker, tmp_path):
    root = tmp_path / "frameworks"
    (root / "Go" / "hugo").mkdir(parents=True)
    (root / "Go" / "hugo" / "benchmark_config.json").write_text("{}")
    (root / "LICENSE").write_text("MIT")
    assert sorted(Metadata(fake_benchmarker).gather_languages()) == ["Go"]
