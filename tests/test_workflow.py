import pathlib

import pytest

yaml = pytest.importorskip("yaml")

WF = pathlib.Path(__file__).parent.parent / ".github" / "workflows" / "benchmark-round.yml"


def _load():
    return yaml.safe_load(WF.read_text())


def test_workflow_suite_input_and_permissions():
    d = _load()
    inputs = d[True]["workflow_dispatch"]["inputs"]
    assert inputs["suite"]["options"] == ["", "smoke", "standard", "stress",
                                          "P", "M", "G", "GG"]
    assert "5" in inputs["content_size"]["options"] and "50" in inputs["content_size"]["options"]
    assert d["permissions"] == {"contents": "read"}


def test_workflow_matrix_from_list_output_and_no_inline_inputs():
    d = _load()
    assert "include" in d["jobs"]["run"]["strategy"]["matrix"]
    text = WF.read_text()
    # inputs reach shell only through env:
    for line in text.splitlines():
        if line.strip().startswith(("run:", "- run:")) or "./ssgberk" in line:
            assert "${{ inputs." not in line and "${{ matrix." not in line
