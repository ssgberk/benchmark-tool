import csv
import io
import json
import pathlib

from toolset.quality import reduce, site
from toolset.utils import summary
from toolset.utils.results import parse_build_output

FIX = pathlib.Path(__file__).parent / "fixtures" / "quality"
RAW_OK = pathlib.Path(__file__).parent / "fixtures" / "raw_ok.txt"


def _quality():
    raw = json.loads((FIX / "raw.json").read_text())
    pages = site.resolve_pages(str(FIX / "site"))
    return reduce.build_quality(raw, str(FIX / "site"), pages, "post/*/index.html")


def _data(with_quality):
    [entry] = parse_build_output(RAW_OK.read_text(), "50", "5", "1")
    data = {"name": "r", "frameworks": ["hugo", "gatsby"],
            "rawData": {"datarate": {"hugo": [entry]}},
            "succeeded": {"datarate": ["hugo"]}, "failed": {"datarate": ["gatsby"]}, "excluded": []}
    if with_quality:
        data["quality"] = {"hugo": _quality(), "gatsby": {"status": "error", "error": "RuntimeError: boom"}}
    return data


def test_quality_rows():
    rows = summary.quality_rows(_data(True))
    assert [r["framework"] for r in rows] == ["gatsby", "hugo"]
    hugo = rows[1]
    assert hugo["performance"] == 0.98 and hugo["lcpMs"] == 800
    assert hugo["postJsBytes"] == 0 and hugo["jsClass"] == "none"
    assert hugo["htmlErrors"] == 1 and hugo["a11yViolations"] == 2 and hugo["brokenLinks"] == 2
    assert (hugo["seoPresent"], hugo["seoTotal"]) == (2, 12)
    assert rows[0]["status"] == "error" and rows[0]["performance"] is None


def test_quality_markdown_section():
    lines = summary.quality_markdown(summary.quality_rows(_data(True)))
    text = "\n".join(lines)
    assert lines[0] == "## Qualidade"
    assert "| hugo | 98 | 100 | 100 | 82 | 800 | 0.0 | none |" in text
    assert "2/12" in text and "no meta description and no viewport" in text
    assert "gatsby: RuntimeError: boom" in text
    assert "Rank" not in text


def test_quality_csv_has_every_numeric_field():
    rows = summary.quality_rows(_data(True))
    parsed = list(csv.DictReader(io.StringIO(summary.quality_csv(rows))))
    assert parsed[1]["framework"] == "hugo"
    header = list(parsed[0].keys())
    assert header[:len(summary.QUALITY_COLUMNS)] == summary.QUALITY_COLUMNS
    assert "lighthouse.desktop.index.scores.seo.median" in header
    assert "weight.brotliBytes" in header


def test_quality_never_changes_timing_summary():
    without, with_q = _data(False), _data(True)
    assert summary.build_rows(with_q, {}) == summary.build_rows(without, {})
    md_without = summary.to_markdown(summary.build_rows(without, {}), without)
    md_with = summary.to_markdown(summary.build_rows(with_q, {}), with_q)
    assert md_with.startswith(md_without.rstrip("\n"))
    assert "## Qualidade" in md_with and "## Qualidade" not in md_without
