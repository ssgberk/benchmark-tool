import csv
import io
import pathlib
import types

from toolset.utils.results import Results, parse_build_output
from toolset.utils.summary import COLUMNS, build_rows, to_csv, to_markdown

FIX = pathlib.Path(__file__).parent / "fixtures"


def _entry(mean, stddev=None):
    [r] = parse_build_output((FIX / "raw_ok.txt").read_text(), "10", "0.500", "1")
    r.update(mean=mean, median=mean, min=mean, max=mean, stddev=stddev)
    return [r]


def _results():
    return {
        "frameworks": ["slow", "fast", "broken", "skipped", "never"],
        "rawData": {"datarate": {"slow": _entry(2.0, 0.1), "fast": _entry(0.12)}},
        "succeeded": {"datarate": ["slow", "fast"]},
        "failed": {"datarate": ["broken"]},
        "excluded": ["skipped"],
    }


LANGS = {"fast": "Go", "slow": "JavaScript"}


def test_rows_order_and_status():
    rows = build_rows(_results(), LANGS)
    assert [r["framework"] for r in rows] == ["fast", "slow", "broken", "never", "skipped"]
    assert [r["status"] for r in rows] == ["ok", "ok", "failed", "failed", "excluded"]
    assert rows[0]["language"] == "Go" and rows[2]["language"] == ""
    assert rows[2]["mean"] == "" and rows[4]["numberOfFiles"] == ""
    assert rows[0]["numberOfFiles"] == "10" and rows[0]["stddev"] == ""


def test_csv_round_trip():
    rows = build_rows(_results(), LANGS)
    parsed = list(csv.DictReader(io.StringIO(to_csv(rows))))
    assert list(parsed[0].keys()) == COLUMNS
    assert len(parsed) == 5 and parsed[1]["mean"] == "2.0" and parsed[2]["status"] == "failed"


def test_markdown_header_rows_and_null_stddev():
    meta = {"name": "run-1", "environmentDescription": "pytest",
            "startTime": 1790000000000, "completionTime": 1790000060000,
            "git": {"commitId": "abc123"}}
    md = to_markdown(build_rows(_results(), LANGS), meta)
    assert "run-1" in md and "pytest" in md and "abc123" in md
    table = [ln for ln in md.splitlines() if ln.startswith("|")]
    assert len(table) == 2 + 5
    assert "0.120" in md and "2.000" in md and "—" in md
    assert "Failed" in md and "- broken" in md and "- never" in md


def test_markdown_without_git_or_failures():
    res = _results()
    res.update(frameworks=["fast"], failed={"datarate": []}, excluded=[])
    md = to_markdown(build_rows(res, LANGS), {"name": "n", "git": None})
    assert "Commit" not in md and "- " not in md.split("Failed")[-1].replace("- none", "")


def test_write_summary_files(fake_benchmarker):
    fake_benchmarker.tests = [types.SimpleNamespace(name="fast", language="Go")]
    res = Results(fake_benchmarker)
    res.report_benchmark_results(fake_benchmarker.tests[0], "datarate", _entry(0.12))
    md = res.write_summary()
    assert "fast" in md
    csv_text = pathlib.Path(res.directory, "summary.csv").read_text()
    assert list(csv.DictReader(io.StringIO(csv_text)))[0]["language"] == "Go"
    assert pathlib.Path(res.directory, "summary.md").read_text() == md
