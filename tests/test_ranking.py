from toolset.utils import ranking


def _row(median, lo, hi):
    return {"median": median, "min": lo, "max": hi}


def test_rank_overlap_ties():
    rows = [_row(2.0, 1.9, 2.1), _row(1.0, 0.9, 1.95), _row(5.0, 4.9, 5.1), _row(3.0, 2.9, 3.1)]
    # sorted: 1.0 (max 1.95), 2.0 (min 1.9 <= 1.95 -> shared), 3.0 (min 2.9 > 2.1), 5.0
    assert ranking.rank(rows) == ["=1", "=1", "4", "3"]  # aligned with input order


def test_rank_blank_median_and_chain():
    rows = [_row("", "", ""), _row(1.0, 0.9, 1.1), _row(1.2, 1.0, 1.3), _row(1.4, 1.25, 1.5)]
    assert ranking.rank(rows) == ["", "=1", "=1", "=1"]


def test_group_key():
    meta = {"suite": {"name": "standard", "version": 1}, "profile": "core",
            "environment": {"fingerprint": "abc"}}
    row = {"numberOfFiles": "100", "contentSize": "0.500", "features": "x"}
    assert ranking.group_key(meta, row) == ("standard", "1", "100", "0.500", "core", "abc", "x")
    other = dict(row, fingerprint="def")
    assert ranking.group_key(meta, other) != ranking.group_key(meta, row)


def test_scaling_exponent_linear():
    b = ranking.scaling_exponent([(100, 1), (1000, 10), (10000, 100)])
    assert "%.2f" % b == "1.00"


def test_scaling_needs_three_points():
    assert ranking.scaling_exponent([(100, 1), (1000, 10)]) is None
    assert ranking.scaling_exponent([]) is None
    assert ranking.scaling_exponent([(100, 1), (100, 2), (100, 3)]) is None


def test_scaling_sublinear():
    assert ranking.scaling_exponent([(10, 5.0), (100, 5.5), (1000, 10)]) < 1
