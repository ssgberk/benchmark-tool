import importlib.util
import pathlib

import pytest

from toolset.benchmark import suites

ROOT = pathlib.Path(__file__).parent.parent
_spec = importlib.util.spec_from_file_location(
    "run_tests", ROOT / "toolset" / "run-tests.py")
run_tests = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_tests)


def pairs(suite):
    return [(c.number_of_files, c.content_size) for c in suite.cells]


def test_standard_cells():
    s = suites.load("standard")
    assert pairs(s) == [(100, "0.500"), (100, "500"), (1000, "0.500"),
                        (1000, "500"), (10000, "0.500")]
    assert s.runs == 5
    assert (10000, "500") not in pairs(s)
    assert s.ranked is True


def test_smoke():
    s = suites.load("smoke")
    assert pairs(s) == [(10, "0.500")]
    assert s.runs == 1


def test_stress():
    s = suites.load("stress")
    assert pairs(s) == [(100000, "0.500"), (10000, "500"),
                        (1000, "1000"), (100, "5000")]
    assert (10000, "500") in pairs(s)
    assert s.runs == 3


def test_legacy_2019():
    s = suites.load("legacy-2019")
    assert len(s.cells) == 7
    assert s.runs == 10
    assert s.ranked is False


def test_invalid_content_size_rejected(tmp_path):
    p = tmp_path / "s.json"
    p.write_text('{"x": {"version": 1, "runs": 1, "cooldownSeconds": 0, '
                 '"timeoutSeconds": 1, "cells": '
                 '[{"numberOfFiles": 1, "contentSize": "7"}]}}')
    with pytest.raises(suites.SuiteError):
        suites.load("x", path=p)


def test_unknown_suite():
    with pytest.raises(suites.SuiteError):
        suites.load("nope")


def test_cell_dir():
    assert suites.cell_dir("core", suites.Cell(1000, "0.500")) == \
        "core/nf1000-cs0.500"


def test_rotate_deterministic():
    names = ["d", "a", "c", "b", "e", "f", "g", "h", "i"]
    assert suites.rotate(names, 0) == sorted(names)
    assert suites.rotate(names, 1) == suites.rotate(names, 1)
    s = sorted(names)
    k = 7 % len(s)
    assert suites.rotate(names, 1) == s[k:] + s[:k]


def test_suite_conflicts_with_nf():
    assert run_tests.main(['x', '--suite', 'smoke', '-nf', '5']) == 1


def test_suite_conflicts_with_cs_and_mr():
    assert run_tests.main(['x', '--suite', 'smoke', '-cs', '500']) == 1
    assert run_tests.main(['x', '--suite', 'smoke', '-mr', '2']) == 1


def test_suite_choices_from_json():
    with pytest.raises(SystemExit):
        run_tests.build_parser().parse_args(['--suite', 'bogus'])


def test_benchmark_test_sh_is_wrapper():
    text = (ROOT / "benchmark_test.sh").read_text()
    assert "--suite" in text
    assert "--clean" not in text


def test_for_cell_and_suite_loop(monkeypatch, tmp_path):
    import json
    import types
    monkeypatch.setenv('FWROOT', str(tmp_path))
    seen = []

    class FakeBenchmarker:
        def __init__(self, config):
            self.config = config
            self.tests = [types.SimpleNamespace(name=n) for n in "cab"]
            self.results = types.SimpleNamespace(
                succeeded={'datarate': ['a']}, failed={'datarate': []})

        def run(self):
            seen.append((self.config.number_of_files, self.config.content_size,
                         self.config.min_runs, self.config.timestamp,
                         self.config.types['datarate'].config is self.config))

        def stop(self, *a):
            pass

    monkeypatch.setattr(run_tests, 'Benchmarker', FakeBenchmarker)
    args = run_tests.build_parser().parse_args(['--suite', 'smoke'])
    assert run_tests.run_suite(args) == 0
    nf, cs, mr, ts, own = seen[0]
    assert (nf, cs, mr, own) == ('10', '0.500', '1', True)
    assert ts.endswith('/core/nf10-cs0.500')
    out = json.loads((tmp_path / 'results' / ts.split('/')[0] / 'suite.json').read_text())
    assert out['suite'] == 'smoke' and out['cells'][0]['order'] == ['a', 'b', 'c']


@pytest.mark.parametrize("flag,val", [("--min", "2"), ("--number", "5"),
                                      ("--content", "500")])
def test_suite_rejects_abbreviated_conflicts(flag, val):
    # abbreviations must not be silently accepted (and ignored) with --suite
    try:
        rc = run_tests.main(['x', '--suite', 'smoke', flag, val])
    except SystemExit as e:
        rc = e.code
    assert rc not in (0, None)


@pytest.mark.parametrize("mode", ["--parse=1", "--clean", "--audit", "--new",
                                  "--list-tests"])
def test_suite_conflicts_with_other_modes(mode):
    assert run_tests.main(['x', '--suite', 'smoke', mode]) == 1


def _fake(monkeypatch, tmp_path, run_result=False, run_raises=None, stop_exits=True):
    import types
    monkeypatch.setenv('FWROOT', str(tmp_path))

    class FB:
        def __init__(self, config):
            self.config = config
            import os
            os.makedirs(os.path.join(config.results_root, config.timestamp))
            self.tests = [types.SimpleNamespace(name='a')]
            self.results = types.SimpleNamespace(
                succeeded={'datarate': []}, failed={'datarate': ['a']})

        def run(self):
            if run_raises:
                raise run_raises
            return run_result

        def stop(self, *a):
            if stop_exits:
                raise SystemExit(0)  # mirrors Benchmarker.stop

    monkeypatch.setattr(run_tests, 'Benchmarker', FB)


def test_suite_fatal_error_exits_nonzero(monkeypatch, tmp_path):
    _fake(monkeypatch, tmp_path, run_raises=RuntimeError("boom"))
    args = run_tests.build_parser().parse_args(['--suite', 'smoke'])
    assert run_tests.run_suite(args) == 1


def test_suite_failed_cell_exits_nonzero(monkeypatch, tmp_path):
    _fake(monkeypatch, tmp_path, run_result=True)
    args = run_tests.build_parser().parse_args(['--suite', 'smoke'])
    assert run_tests.run_suite(args) == 1


def test_suite_interrupt_exits_nonzero(monkeypatch, tmp_path):
    _fake(monkeypatch, tmp_path, run_raises=KeyboardInterrupt())
    args = run_tests.build_parser().parse_args(['--suite', 'smoke'])
    assert run_tests.run_suite(args) != 0


def test_suite_profile_consistent(monkeypatch, tmp_path):
    import json
    _fake(monkeypatch, tmp_path)
    args = run_tests.build_parser().parse_args(
        ['--suite', 'smoke', '--profile', 'extended'])
    run_tests.run_suite(args)
    (suite_json,) = (tmp_path / 'results').glob('*/suite.json')
    out = json.loads(suite_json.read_text())
    assert out['profile'] == 'extended'
    assert out['cells'][0]['dir'] == 'extended/nf10-cs0.500'
    assert (suite_json.parent / out['cells'][0]['dir']).is_dir()
