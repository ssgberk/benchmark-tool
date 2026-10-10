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
        "post": {"url": "/post/hello/", "file": "post/hello/index.html"},
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
    assert pages["post"] == {"url": url, "file": file}


def test_resolve_pages_without_post_link(tmp_path):
    (tmp_path / "index.html").write_text('<a href="/x/">x</a>')
    with pytest.raises(ValueError, match="post-item"):
        site.resolve_pages(str(tmp_path))


def test_resolve_pages_link_to_missing_file(tmp_path):
    (tmp_path / "index.html").write_text('<li class="post-item"><a href="/gone/">g</a></li>')
    with pytest.raises(ValueError, match="no file"):
        site.resolve_pages(str(tmp_path))


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
