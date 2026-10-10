import pathlib

from toolset.quality import seo, site

SITE = pathlib.Path(__file__).parent / "fixtures" / "quality" / "site"

RICH = """<!doctype html><html lang="pt-BR"><head>
<title>Post title</title>
<meta name="description" content="A post about things">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="canonical" href="https://example.org/post/a/">
<meta property="og:title" content="Post title"><meta property="og:description" content="d">
<meta property="og:type" content="article"><meta property="og:url" content="https://example.org/post/a/">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index,follow">
<link rel="alternate" hreflang="en" href="/en/"><link rel="alternate" hreflang="pt" href="/pt/">
<link rel="icon" href="/favicon.svg">
<script type="application/ld+json">{"@type": "BlogPosting"}</script>
</head><body><h1>T</h1><h2>S</h2><img src="a.png" alt="a"><img src="d.png" alt=""></body></html>"""


def test_reference_page_has_only_title_and_lang():
    s = seo.page_signals((SITE / "post" / "hello" / "index.html").read_text())
    assert s["title"] is True and s["titleLength"] == 5 and s["lang"] == "en"
    assert s["description"] is False and s["viewport"] is False and s["canonical"] is False
    assert s["jsonLd"] is False and s["jsonLdValid"] is None and s["robotsMeta"] is None
    assert s["h1"] == 1 and s["headingSkip"] is False and s["imgWithoutAlt"] == 0
    assert s["present"] == 2


def test_rich_page_has_every_signal():
    s = seo.page_signals(RICH)
    assert s["present"] == len(seo.PAGE_SIGNALS) == 12
    assert s["descriptionLength"] == len("A post about things")
    assert s["robotsMeta"] == "index,follow" and s["hreflang"] == 2
    assert s["jsonLdBlocks"] == 1 and s["jsonLdValid"] is True
    assert s["faviconLink"] is True and s["imgWithoutAlt"] == 0


def test_broken_json_ld():
    s = seo.page_signals('<script type="application/ld+json">{not json</script>')
    assert s["jsonLd"] is True and s["jsonLdValid"] is False


def test_heading_skip_images_and_empty_links():
    html = ('<h1>a</h1><h3>b</h3><img src="x.png"><img src="y.png" alt="">'
            '<a href="/1"></a><a href="/2" aria-label="Two"></a>'
            '<a href="/3"><img src="l.png" alt="logo"></a><a href="/4"> </a><a>no href</a>')
    s = seo.page_signals(html)
    assert s["headingSkip"] is True
    assert s["imgWithoutAlt"] == 1
    assert s["emptyLinks"] == 2


def test_page_signals_malformed_html():
    html = b"<html lang=en><title>x</title><div><p>unclosed \xff\xfe".decode("utf-8", "replace")
    s = seo.page_signals(html)
    assert s["title"] is True and s["lang"] == "en"


def test_site_signals(tmp_path):
    (tmp_path / "robots.txt").write_text("User-agent: *\n")
    (tmp_path / "sitemap.xml").write_text(
        '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        '<url><loc>/a/</loc></url><url><loc>/b/</loc></url></urlset>')
    (tmp_path / "feed.xml").write_text("<rss/>")
    (tmp_path / "favicon.ico").write_bytes(b"\x00")
    s = seo.site_signals(str(tmp_path), [])
    assert s == {"robotsTxt": True, "sitemap": {"present": True, "valid": True, "urls": 2},
                 "feed": True, "favicon": True}


def test_site_signals_invalid_sitemap_and_link_favicon(tmp_path):
    (tmp_path / "sitemap.xml").write_text("<urlset><url>")
    s = seo.site_signals(str(tmp_path), [{"faviconLink": True}])
    assert s["sitemap"] == {"present": True, "valid": False, "urls": None}
    assert s["favicon"] is True and s["robotsTxt"] is False and s["feed"] is False


def test_seo_section_fixture():
    pages = site.resolve_pages(str(SITE))
    section = seo.seo_section(str(SITE), pages)
    assert section["total"] == 12
    assert section["present"] == {"index": 2, "post": 2, "404": 2}
    assert section["site"]["feed"] is True and section["site"]["sitemap"]["present"] is False
    assert set(section["pages"]) == {"index", "post", "404"}
