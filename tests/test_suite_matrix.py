import json

import pytest

from toolset.github_actions import suite_matrix


def test_matrix_is_generator_by_cell():
    m = suite_matrix.build_matrix("M", ["hugo", "zola"])
    assert len(m) == 4
    assert {(e["test"], e["cell"]) for e in m} == {
        ("hugo", 0), ("hugo", 1), ("zola", 0), ("zola", 1)}
    e = next(x for x in m if x["test"] == "zola" and x["cell"] == 1)
    assert (e["number_of_files"], e["content_size"], e["min_runs"]) == ("1000", "50", "5")
    assert e["suite"] == "M" and e["key"] == "zola-M-1"


def test_matrix_17_generators_two_cells_under_limit():
    assert len(suite_matrix.build_matrix("GG", ["g%d" % i for i in range(17)])) == 34


def test_matrix_over_limit_rejected():
    with pytest.raises(ValueError):
        suite_matrix.build_matrix("standard", ["g%d" % i for i in range(60)])


def test_matrix_unknown_suite():
    with pytest.raises(ValueError):
        suite_matrix.build_matrix("nope", ["a"])


def test_cli_prints_json(capsys):
    assert suite_matrix.main(["--suite", "P", "--tests", "a", "b"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 4


@pytest.mark.parametrize("name", ["smoke", "standard", "stress", "P", "M", "G", "GG"])
def test_matrix_job_timeout_covers_suite_timeout(name):
    suite = suite_matrix.suites.load(name)
    for e in suite_matrix.build_matrix(name, ["hugo"]):
        if suite.runs >= 3:
            # a noise re-run can follow the first attempt: use the hosted maximum
            assert e["timeout_minutes"] == 360
        else:
            assert e["timeout_minutes"] == min(360, -(-suite.timeout_seconds // 60) + 30)


def test_matrix_job_timeout_values():
    assert suite_matrix.build_matrix("GG", ["a"])[0]["timeout_minutes"] == 330
    assert suite_matrix.build_matrix("smoke", ["a"])[0]["timeout_minutes"] == 60
    assert suite_matrix.build_matrix("P", ["a"])[0]["timeout_minutes"] == 360


def test_matrix_job_timeout_capped_for_long_single_run_suite():
    suite = suite_matrix.suites.Suite(name="X", version=1, runs=1, cooldown_seconds=0,
                                      timeout_seconds=6 * 3600)
    assert suite_matrix.job_timeout_minutes(suite) == 360


def test_matrix_cell_is_index_into_suite_cells():
    suite = suite_matrix.suites.load("standard")
    m = suite_matrix.build_matrix("standard", ["hugo"])
    assert [e["cell"] for e in m] == list(range(len(suite.cells)))
