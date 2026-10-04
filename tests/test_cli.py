import importlib.util
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "run_tests", pathlib.Path(__file__).parent.parent / "toolset" / "run-tests.py")
run_tests = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_tests)


def parse(*argv):
    return run_tests.build_parser().parse_args(list(argv))


def test_cs_default_is_half_kb():
    assert parse().content_size == "0.500"


def test_cs_accepts_100000_as_single_value():
    assert parse("-cs", "100000").content_size == "100000"


def test_cs_rejects_unknown():
    with pytest.raises(SystemExit):
        parse("-cs", "7")


def test_verbose_is_flag():
    assert parse("-v").verbose is True
    assert parse().verbose is False


def test_help_texts_are_specific():
    helps = {a.dest: a.help for a in run_tests.build_parser()._actions}
    assert "number of" in helps["number_of_files"].lower()
    assert "kb" in helps["content_size"].lower()
    assert "runs" in helps["min_runs"].lower()
