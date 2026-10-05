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
