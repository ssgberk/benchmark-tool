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


def test_suite_rounds_run_one_suite_cell():
    d = _load()
    run = d["jobs"]["run"]
    step = next(s for s in run["steps"] if s.get("name") == "Run benchmark")
    assert step["env"]["SUITE"] == "${{ matrix.suite }}"
    assert step["env"]["CELL"] == "${{ matrix.cell }}"
    assert '--suite "$SUITE" --cell "$CELL"' in step["run"]
    # ad-hoc dispatch keeps working
    assert '-nf "$NF" -cs "$CS" -mr "$MR"' in step["run"]
    assert run["timeout-minutes"] == "${{ matrix.timeout_minutes }}"


def test_adhoc_matrix_keeps_full_job_timeout():
    step = _load()["jobs"]["list"]["steps"][1]
    assert "timeout_minutes: 360" in step["run"]


def test_result_dir_finds_nested_suite_cell():
    d = _load()
    step = next(s for s in d["jobs"]["run"]["steps"]
                if s.get("name") == "Record runner environment")
    assert "results/*/*/nf*-cs*/" in step["run"]
