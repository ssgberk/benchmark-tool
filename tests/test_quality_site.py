import io
import json
import pathlib
import tarfile

import pytest

from toolset.quality import site

SITE = pathlib.Path(__file__).parent / "fixtures" / "quality" / "site"


def test_generator_config(tmp_path):
    (tmp_path / "benchmark_config.json").write_text(json.dumps(
        {"framework": "hugo", "config": [{"output_folder": "public", "output_glob": "post/*/index.html"}]}))
    assert site.generator_config(str(tmp_path)) == ("public", "post/*/index.html")


def _tar(entries):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            if data is None:
                info.type = tarfile.DIRTYPE
                tar.addfile(info)
            else:
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_extract_strips_top_dir(tmp_path):
    tar_path = tmp_path / "site.tar"
    tar_path.write_bytes(_tar([("public", None), ("public/index.html", b"<p>i</p>"),
                               ("public/post/a/index.html", b"<p>a</p>")]))
    dest = tmp_path / "site"
    assert site.extract(str(tar_path), str(dest)) == str(dest)
    assert (dest / "index.html").read_bytes() == b"<p>i</p>"
    assert (dest / "post" / "a" / "index.html").exists()


def test_extract_rejects_path_traversal(tmp_path):
    tar_path = tmp_path / "site.tar"
    tar_path.write_bytes(_tar([("public/../../evil.html", b"x")]))
    with pytest.raises(tarfile.TarError):
        site.extract(str(tar_path), str(tmp_path / "site"))
    assert not (tmp_path.parent / "evil.html").exists()


def test_resolve_pages_fixture():
    assert site.resolve_pages(str(SITE)) == {
        "index": {"url": "/", "file": "index.html"},
        "post": {"url": "/post/hello/", "file": "post/hello/index.html", "source": "index"},
        "404": {"url": "/404.html", "file": "404.html"},
    }


@pytest.mark.parametrize("href,url,file", [
    ("/post/a/", "/post/a/", "post/a/index.html"),
    ("post/a/", "/post/a/", "post/a/index.html"),
    ("./post/a/index.html", "/post/a/index.html", "post/a/index.html"),
    ("/post/a?x=1#t", "/post/a", "post/a/index.html"),
    ("/post/a", "/post/a", "post/a/index.html"),
    ("/post/b", "/post/b", "post/b.html"),
])
def test_resolve_pages_variants(tmp_path, href, url, file):
    (tmp_path / "post" / "a").mkdir(parents=True)
    (tmp_path / "post" / "a" / "index.html").write_text("a")
    (tmp_path / "post" / "b.html").write_text("b")
    (tmp_path / "index.html").write_text(
        '<ul><li class="post-item"><a href="%s">A</a></li></ul>' % href)
    pages = site.resolve_pages(str(tmp_path))
    assert pages["post"] == {"url": url, "file": file, "source": "index"}


def test_resolve_pages_without_post_link(tmp_path):
    (tmp_path / "index.html").write_text('<a href="/x/">x</a>')
    with pytest.raises(ValueError, match="post-item"):
        site.resolve_pages(str(tmp_path))


def test_resolve_pages_link_to_missing_file_without_glob(tmp_path):
    (tmp_path / "index.html").write_text('<li class="post-item"><a href="/gone/">g</a></li>')
    with pytest.raises(ValueError, match="post-item"):
        site.resolve_pages(str(tmp_path))


def _site(tmp_path, index, files):
    (tmp_path / "index.html").write_text(index)
    for f in files:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("x")


def test_resolve_pages_glob_fallback_dir_style(tmp_path):
    _site(tmp_path, '<a href="/x/">x</a>', ["post/b/index.html", "post/a/index.html", "404.html"])
    pages = site.resolve_pages(str(tmp_path), "post/*/index.html")
    assert pages["post"] == {"url": "/post/a/", "file": "post/a/index.html", "source": "glob"}
    assert pages["404"] == {"url": "/404.html", "file": "404.html"}


def test_resolve_pages_glob_fallback_html_style(tmp_path):
    _site(tmp_path, "<p>none</p>", ["posts/b.html", "posts/a.html"])
    pages = site.resolve_pages(str(tmp_path), "posts/*.html")
    assert pages["post"] == {"url": "/posts/a.html", "file": "posts/a.html", "source": "glob"}


def test_resolve_pages_missing_link_target_falls_back_to_glob(tmp_path):
    _site(tmp_path, '<li class="post-item"><a href="/gone/">g</a></li>', ["post/a/index.html"])
    pages = site.resolve_pages(str(tmp_path), "post/*/index.html")
    assert pages["post"]["source"] == "glob" and pages["post"]["url"] == "/post/a/"


def test_resolve_pages_no_404_file(tmp_path):
    _site(tmp_path, '<li class="post-item"><a href="/post/a/">a</a></li>', ["post/a/index.html"])
    pages = site.resolve_pages(str(tmp_path), "post/*/index.html")
    assert set(pages) == {"index", "post"}


def test_resolve_pages_nothing_found(tmp_path):
    _site(tmp_path, "<p>none</p>", ["other/file.txt"])
    with pytest.raises(ValueError, match=r"post-item.*post/\*/index\.html"):
        site.resolve_pages(str(tmp_path), "post/*/index.html")


def test_resolve_pages_requires_index(tmp_path):
    with pytest.raises(ValueError, match="index.html"):
        site.resolve_pages(str(tmp_path), "*.html")


def test_list_files_is_sorted_posix():
    files = site.list_files(str(SITE))
    assert files == sorted(files) and "post/hello/index.html" in files


def test_extra_output_fixture():
    extra = site.extra_output(str(SITE), "post/*/index.html")
    assert extra["files"] == 2
    assert set(extra["byExtension"]) == {".html", ".xml"}
    assert extra["byExtension"][".html"]["files"] == 1
    assert extra["bytes"] == sum(e["bytes"] for e in extra["byExtension"].values())


def test_works_without_js():
    post = "post/hello/index.html"
    rendered = {"title": "Hello", "firstParagraph": "First paragraph of the post."}
    assert site.works_without_js(str(SITE), post, rendered) is True
    assert site.works_without_js(str(SITE), post, {"title": "Hello", "firstParagraph": "Only after JS"}) is False
    assert site.works_without_js(str(SITE), post, None) is None
    assert site.works_without_js(str(SITE), post, {"error": "boom"}) is None


def test_text_of_collapses_whitespace():
    assert site.text_of("<p>a\n  <b>b</b></p><script>x()</script>") == "a b"


def test_text_of_keeps_inline_punctuation():
    assert site.text_of("<p>See <a>x</a>.</p>") == "See x."


def test_works_without_js_inline_markup(tmp_path):
    (tmp_path / "post.html").write_text(
        '<!doctype html><html><head><title>T</title></head><body>'
        '<h1 class="post-title">T</h1><div class="post-body"><p>See <a href="/">x</a>.</p></div>'
        '</body></html>')
    rendered = {"title": "T", "firstParagraph": "See x."}
    assert site.works_without_js(str(tmp_path), "post.html", rendered) is True
