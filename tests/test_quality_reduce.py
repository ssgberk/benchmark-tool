import json
import pathlib

from toolset.quality import reduce, site

FIX = pathlib.Path(__file__).parent / "fixtures" / "quality"
SITE = FIX / "site"
GLOB = "post/*/index.html"


def _raw():
    return json.loads((FIX / "raw.json").read_text())


def test_spread():
    assert reduce.spread([3, 1, 2]) == {"median": 2, "min": 1, "max": 3}
    assert reduce.spread([None, 4]) == {"median": 4, "min": 4, "max": 4}
    assert reduce.spread([None]) is None


def test_reduce_lighthouse_median_and_median_run_audits():
    lh = reduce.reduce_lighthouse(_raw()["lighthouse"])
    post = lh["mobile"]["post"]
    assert post["status"] == "ok" and post["runs"] == 3
    assert post["scores"]["performance"] == {"median": 0.98, "min": 0.97, "max": 0.99}
    assert post["metrics"]["lcp"] == {"median": 800, "min": 700, "max": 900}
    # the run whose performance is the median (0.98) failed audit "b"
    assert post["failedAudits"] == ["b"]
    assert set(lh) == {"mobile", "desktop"}


def test_reduce_lighthouse_page_errors():
    raw = {"mobile": {"index": {"error": "chrome died"},
                      "post": [{"error": "timeout"}, {"error": "timeout"}],
                      "404": [{"error": "x"}, _raw()["lighthouse"]["mobile"]["post"][0]]},
           "desktop": {}}
    lh = reduce.reduce_lighthouse(raw)
    assert lh["mobile"]["index"] == {"status": "error", "error": "chrome died"}
    assert lh["mobile"]["post"] == {"status": "error", "error": "timeout"}
    assert lh["mobile"]["404"]["status"] == "ok" and lh["mobile"]["404"]["runs"] == 1


def test_reduce_axe_counts_by_impact():
    a = reduce.reduce_axe(_raw()["axe"])
    assert a["post"] == {"violations": {"critical": 0, "serious": 1, "moderate": 1, "minor": 0},
                         "total": 2, "rules": ["color-contrast", "region"]}
    assert a["index"]["total"] == 0
    assert reduce.reduce_axe({"index": {"error": "boom"}})["index"] == {"status": "error", "error": "boom"}


def test_reduce_html_counts():
    h = reduce.reduce_html(_raw()["html"])
    assert h["post"] == {"errors": 1, "warnings": 1, "rules": ["no-inline-style", "prefer-native-element"]}


def test_reduce_links_kinds():
    links = reduce.reduce_links(_raw()["links"])
    assert links["broken"] == 2
    assert links["byKind"] == {"link": 0, "anchor": 1, "asset": 1}
    assert links["items"][0]["status"] == "Cannot find file"


def test_reduce_links_caps_items():
    fail = {"s": [{"url": "/p%d/" % i, "status": {"text": "x"}} for i in range(30)]}
    links = reduce.reduce_links({"report": {"fail_map": fail}})
    assert links["broken"] == 30 and len(links["items"]) == reduce.MAX_BROKEN_LISTED == 20


def test_weight():
    files = [{"path": "index.html", "bytes": 100, "gzip": 50, "br": 40},
             {"path": "post/a/index.html", "bytes": 300, "gzip": 100, "br": 90},
             {"path": "post/b/index.html", "bytes": 100, "gzip": 60, "br": 50},
             {"path": "assets/ssgberk.css", "bytes": 1000, "gzip": 400, "br": 300}]
    assert reduce.weight(files, GLOB) == {"bytes": 1500, "gzipBytes": 610, "brotliBytes": 480,
                                          "bytesPerPost": 200, "generatorAddedBytes": 500}


def test_js_section_classes():
    lh = {"mobile": {"index": {"status": "ok", "resources": {"jsBytes": {"median": 0}}},
                     "post": {"status": "ok", "resources": {"jsBytes": {"median": 0}}}}}
    files = [{"path": "a.js", "bytes": 10, "gzip": 5, "br": 4}]
    js = reduce.js_section(lh, files, True)
    assert js == {"pages": {"index": 0, "post": 0}, "diskBytes": 10, "jsClass": "none", "worksWithoutJs": True}
    lh["mobile"]["post"]["resources"]["jsBytes"]["median"] = 5000
    assert reduce.js_section(lh, files, False)["jsClass"] == "hydrated"
    assert reduce.js_section({"mobile": {}}, [], None)["jsClass"] is None


def test_build_quality_fixture_all_ok():
    pages = site.resolve_pages(str(SITE))
    q = reduce.build_quality(_raw(), str(SITE), pages, GLOB)
    assert q["status"] == "ok"
    assert q["pages"] == {"index": "/", "post": "/post/hello/", "404": "/404.html"}
    for section in reduce.SECTIONS:
        assert q[section]["status"] == "ok", (section, q[section])
    assert q["js"]["worksWithoutJs"] is True and q["js"]["jsClass"] == "none"
    assert q["extra"]["files"] == 2 and q["seo"]["present"]["post"] == 2


def test_build_quality_partial_errors():
    raw = _raw()
    raw["lighthouse"] = {"error": "lighthouse crashed"}
    del raw["links"]
    raw["files"] = {"error": "EACCES"}
    pages = site.resolve_pages(str(SITE))
    q = reduce.build_quality(raw, str(SITE), pages, GLOB)
    assert q["lighthouse"] == {"status": "error", "error": "RuntimeError: lighthouse crashed"}
    assert q["links"]["status"] == "error" and "missing" in q["links"]["error"]
    assert q["weight"]["status"] == "error" and q["js"]["status"] == "error"
    for section in ("seo", "html", "a11y", "extra"):
        assert q[section]["status"] == "ok"
    assert q["status"] == "ok"
