# 009 Output Quality: Tasks

Read `spec.md` and `plan.md` (Global Constraints, Contracts, Decisions) first. Every task's requirements include the Global Constraints. Run commands from the repository root. Commit with `git commit -S` as configured; never pass `--no-gpg-sign` or `--author`. End every commit message with:

```
Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
```

Test command (no Docker): `python3 -m pytest -q` and `ruff check toolset tests`.

---

### Task 1: Site helpers (`toolset/quality/site.py`)

**Files:**
- Create: `toolset/quality/__init__.py` (empty), `toolset/quality/site.py`
- Create: `tests/fixtures/quality/site/index.html`, `tests/fixtures/quality/site/post/hello/index.html`, `tests/fixtures/quality/site/404.html`, `tests/fixtures/quality/site/assets/ssgberk.css`, `tests/fixtures/quality/site/assets/ssgberk.png`, `tests/fixtures/quality/site/tags/a/index.html`, `tests/fixtures/quality/site/feed.xml`
- Test: `tests/test_quality_site.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `REFERENCE_ASSETS`
  - `generator_config(test_directory) -> (str, str)`
  - `extract(tar_path, dest) -> str`
  - `url_to_file(site_dir, url) -> str | None`
  - `resolve_pages(site_dir) -> dict`
  - `list_files(site_dir) -> list[str]`
  - `extra_output(site_dir, output_glob) -> dict` (no `status` key)
  - `works_without_js(site_dir, post_file, rendered) -> bool | None`
  - `text_of(html) -> str`, which collapses the visible text of an HTML string.

- [ ] **Step 1: Write the fixture site**

`tests/fixtures/quality/site/index.html`:

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>SSGBerk Reference</title>
<link rel="stylesheet" href="/assets/ssgberk.css"></head>
<body>
<header class="site-header"><a class="site-title" href="/">SSGBerk Reference</a>
<nav class="site-nav"><ul><li><a href="/" aria-current="page">Home</a></li><li><a href="/#posts">Posts</a></li><li><a href="https://github.com/ssgberk">Source</a></li></ul></nav></header>
<main class="site-main"><section id="posts"><ul class="post-list">
<li class="post-item"><a class="post-item-link" href="/post/hello/">Hello</a></li>
</ul></section></main>
<footer class="site-footer"><p>Built for the SSGBerk build-time benchmark.</p></footer>
</body>
</html>
```

`tests/fixtures/quality/site/post/hello/index.html`:

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Hello</title>
<link rel="stylesheet" href="/assets/ssgberk.css"></head>
<body>
<header class="site-header"><a class="site-title" href="/">SSGBerk Reference</a>
<nav class="site-nav"><ul><li><a href="/">Home</a></li><li><a href="/#posts">Posts</a></li><li><a href="https://github.com/ssgberk">Source</a></li></ul></nav></header>
<main class="site-main"><article class="post">
<h1 class="post-title">Hello</h1>
<p class="post-meta"><time class="post-date" datetime="2026-01-01">2026-01-01</time> <span class="post-author">SSGBerk</span></p>
<ul class="post-tags"><li class="post-tag">a</li><li class="post-tag">b</li><li class="post-tag">c</li></ul>
<div class="post-body"><p>First paragraph of the post.</p><p>Second paragraph.</p></div>
</article></main>
<footer class="site-footer"><p>Built for the SSGBerk build-time benchmark.</p></footer>
</body>
</html>
```

`tests/fixtures/quality/site/404.html`:

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Not found</title>
<link rel="stylesheet" href="/assets/ssgberk.css"></head>
<body>
<header class="site-header"><a class="site-title" href="/">SSGBerk Reference</a>
<nav class="site-nav"><ul><li><a href="/">Home</a></li><li><a href="/#posts">Posts</a></li><li><a href="https://github.com/ssgberk">Source</a></li></ul></nav></header>
<main class="site-main"><h1>Page not found</h1></main>
<footer class="site-footer"><p>Built for the SSGBerk build-time benchmark.</p></footer>
</body>
</html>
```

`tests/fixtures/quality/site/assets/ssgberk.css`:

```css
body { font-family: sans-serif; margin: 0 auto; max-width: 40rem; }
```

`tests/fixtures/quality/site/tags/a/index.html` (extra output):

```html
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Tag a</title></head><body><p>a</p></body></html>
```

`tests/fixtures/quality/site/feed.xml` (extra output):

```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>SSGBerk Reference</title></channel></rss>
```

Write the 1×1 PNG with Python:

```bash
python3 - <<'EOF'
import struct, zlib
def chunk(t, d):
    return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
       + chunk(b'IDAT', zlib.compress(b'\x00\xff\xff\xff')) + chunk(b'IEND', b''))
open('tests/fixtures/quality/site/assets/ssgberk.png', 'wb').write(png)
EOF
```

- [ ] **Step 2: Write the failing tests**

`tests/test_quality_site.py`:

```python
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
```

- [ ] **Step 3: Run them and see them fail**

Run: `python3 -m pytest -q tests/test_quality_site.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'toolset.quality'`.

- [ ] **Step 4: Implement `toolset/quality/site.py`**

```python
'''
Pages and files of a generated site (spec 009 R-3, R-7, R-14, R-15).
'''
import fnmatch
import json
import os
import posixpath
import re
import tarfile
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

# SF 005 reference assets: every generator ships them unchanged (R-13, R-15)
REFERENCE_ASSETS = ('assets/ssgberk.css', 'assets/ssgberk.png')


def generator_config(test_directory):
    '''(output_folder, output_glob) of benchmark_config.json config[0].'''
    with open(os.path.join(test_directory, 'benchmark_config.json')) as f:
        config = json.load(f)['config'][0]
    return config['output_folder'], config['output_glob']


def extract(tar_path, dest):
    '''
    Extracts the archive DockerHelper.benchmark exported (a single top
    directory named after output_folder) into dest, without that directory.
    '''
    os.makedirs(dest, exist_ok=True)
    with tarfile.open(tar_path) as tar:
        members = []
        for member in tar.getmembers():
            parts = member.name.split('/', 1)
            if len(parts) < 2 or not parts[1]:
                continue
            member.name = parts[1]
            members.append(member)
        # filter='data' rejects absolute paths, '..' and links out of dest
        tar.extractall(dest, members=members, filter='data')
    return dest


def url_to_file(site_dir, url):
    '''The file a static server would return for url, or None.'''
    p = unquote(urlsplit(url).path).lstrip('/')
    if p == '' or p.endswith('/'):
        candidates = [posixpath.join(p, 'index.html')]
    else:
        candidates = [p, p + '/index.html', p + '.html']
    for c in candidates:
        if os.path.isfile(os.path.join(site_dir, c)):
            return posixpath.normpath(c)
    return None


class _PostLink(HTMLParser):
    '''First a[href] after the first element whose class list has post-item.'''

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_item = False
        self.href = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or '') for k, v in attrs}
        if 'post-item' in a.get('class', '').split():
            self.in_item = True
        if tag == 'a' and self.in_item and self.href is None and a.get('href'):
            self.href = a['href']


def _read(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def resolve_pages(site_dir):
    '''The three audited pages (R-7): index, first post link, 404.'''
    parser = _PostLink()
    parser.feed(_read(os.path.join(site_dir, 'index.html')))
    if not parser.href:
        raise ValueError('no a[href] inside .post-item on the index')
    path = urlsplit(parser.href).path
    url = posixpath.normpath(posixpath.join('/', path))
    if path.endswith('/') and url != '/':
        url += '/'
    post_file = url_to_file(site_dir, url)
    if post_file is None:
        raise ValueError('post link %s matches no file' % parser.href)
    return {
        'index': {'url': '/', 'file': 'index.html'},
        'post': {'url': url, 'file': post_file},
        '404': {'url': '/404.html', 'file': '404.html'},
    }


def list_files(site_dir):
    out = []
    for root, _dirs, files in os.walk(site_dir):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), site_dir)
            out.append(rel.replace(os.sep, '/'))
    return sorted(out)


def extra_output(site_dir, output_glob):
    '''R-15: files outside the SF 005 page set, by extension.'''
    by_ext = {}
    total_files = total_bytes = 0
    for f in list_files(site_dir):
        if f in ('index.html', '404.html') or f in REFERENCE_ASSETS \
                or fnmatch.fnmatch(f, output_glob):
            continue
        size = os.path.getsize(os.path.join(site_dir, f))
        ext = os.path.splitext(f)[1].lower() or '(none)'
        entry = by_ext.setdefault(ext, {'files': 0, 'bytes': 0})
        entry['files'] += 1
        entry['bytes'] += size
        total_files += 1
        total_bytes += size
    return {'files': total_files, 'bytes': total_bytes,
            'byExtension': dict(sorted(by_ext.items()))}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'template'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template') and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def text_of(html):
    parser = _Text()
    parser.feed(html)
    parser.close()
    return re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip()


def works_without_js(site_dir, post_file, rendered):
    '''
    R-14: True when the static post HTML already holds the title and first
    body paragraph that the browser shows after scripts ran.
    '''
    if not isinstance(rendered, dict) or 'error' in rendered:
        return None
    title = re.sub(r'\s+', ' ', rendered.get('title') or '').strip()
    first = re.sub(r'\s+', ' ', rendered.get('firstParagraph') or '').strip()
    if not title or not first:
        return None
    static = text_of(_read(os.path.join(site_dir, post_file)))
    return title in static and first in static
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m pytest -q tests/test_quality_site.py && ruff check toolset tests`
Expected: all pass, no ruff findings.

- [ ] **Step 6: Commit**

```bash
git add toolset/quality/__init__.py toolset/quality/site.py tests/test_quality_site.py tests/fixtures/quality/site
git commit -m "feat(quality): site helpers for the output quality pass (spec 009)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: SEO signals (`toolset/quality/seo.py`)

**Files:**
- Create: `toolset/quality/seo.py`
- Test: `tests/test_quality_seo.py`

**Interfaces:**
- Consumes: `site.list_files`, `site._read` (Task 1); the fixture site.
- Produces:
  - `PAGE_SIGNALS`
  - `page_signals(html) -> dict`
  - `site_signals(site_dir, page_signals_list) -> dict`
  - `seo_section(site_dir, pages) -> {"total", "pages", "present", "site"}` (no `status` key)

- [ ] **Step 1: Write the failing tests**

`tests/test_quality_seo.py`:

```python
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
```

- [ ] **Step 2: Run them and see them fail**

Run: `python3 -m pytest -q tests/test_quality_seo.py`
Expected: FAIL with `ImportError: cannot import name 'seo'`.

- [ ] **Step 3: Implement `toolset/quality/seo.py`**

```python
'''
SEO signals of a generated page and site (spec 009 R-9). Reported, not scored.
'''
import json
import os
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from toolset.quality import site

# The per-page signals counted in seo.present (out of len(PAGE_SIGNALS))
PAGE_SIGNALS = ('title', 'lang', 'description', 'viewport', 'canonical', 'ogTitle',
                'ogDescription', 'ogType', 'ogUrl', 'twitterCard', 'jsonLd', 'robotsMeta')
META = {('name', 'description'): 'description', ('name', 'viewport'): 'viewport',
        ('property', 'og:title'): 'ogTitle', ('property', 'og:description'): 'ogDescription',
        ('property', 'og:type'): 'ogType', ('property', 'og:url'): 'ogUrl',
        ('name', 'twitter:card'): 'twitterCard', ('name', 'robots'): 'robotsMeta'}
FEEDS = ('feed.xml', 'atom.xml', 'rss.xml', 'index.xml', 'feed/index.xml', 'rss/index.xml')
FAVICONS = ('favicon.ico', 'favicon.svg', 'favicon.png')


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = None
        self.meta = {}
        self.canonical = None
        self.hreflang = 0
        self.favicon_link = False
        self.jsonld = []
        self.headings = []
        self.img_without_alt = 0
        self.empty_links = 0
        self._capture = None  # 'title' or 'jsonld'
        self._buf = []
        self._links = []  # one bool per open <a href>: has an accessible name

    def handle_starttag(self, tag, attrs):
        a = {k: (v or '') for k, v in attrs}
        if tag == 'html' and a.get('lang'):
            self.lang = a['lang']
        elif tag == 'title' and self.title is None:
            self._capture, self._buf = 'title', []
        elif tag == 'meta':
            for (attr, value), key in META.items():
                if a.get(attr, '').lower() == value:
                    self.meta[key] = a.get('content', '')
        elif tag == 'link':
            rel = a.get('rel', '').lower().split()
            if 'canonical' in rel and a.get('href'):
                self.canonical = a['href']
            if 'alternate' in rel and 'hreflang' in a:
                self.hreflang += 1
            if 'icon' in rel:
                self.favicon_link = True
        elif tag == 'script' and a.get('type', '').lower() == 'application/ld+json':
            self._capture, self._buf = 'jsonld', []
        elif re.fullmatch(r'h[1-6]', tag):
            self.headings.append(int(tag[1]))
        elif tag == 'img':
            if 'alt' not in a:
                self.img_without_alt += 1
            elif a['alt'].strip() and self._links:
                self._links[-1] = True
        elif tag == 'a' and 'href' in a:
            self._links.append(bool(a.get('aria-label', '').strip() or a.get('title', '').strip()))

    def handle_endtag(self, tag):
        if tag == 'title' and self._capture == 'title':
            self.title = ''.join(self._buf).strip()
            self._capture = None
        elif tag == 'script' and self._capture == 'jsonld':
            self.jsonld.append(''.join(self._buf))
            self._capture = None
        elif tag == 'a' and self._links:
            if not self._links.pop():
                self.empty_links += 1

    def handle_data(self, data):
        if self._capture:
            self._buf.append(data)
        if self._links and data.strip():
            self._links[-1] = True


def _skips(levels):
    return any(b > a + 1 for a, b in zip(levels, levels[1:]))


def page_signals(html):
    c = _Collector()
    c.feed(html)
    c.close()
    valid = []
    for block in c.jsonld:
        try:
            json.loads(block)
            valid.append(True)
        except ValueError:
            valid.append(False)
    s = {
        'title': bool(c.title),
        'titleLength': len(c.title or ''),
        'lang': c.lang,
        'description': bool(c.meta.get('description')),
        'descriptionLength': len(c.meta.get('description', '')),
        'viewport': 'viewport' in c.meta,
        'canonical': bool(c.canonical),
        'ogTitle': 'ogTitle' in c.meta,
        'ogDescription': 'ogDescription' in c.meta,
        'ogType': 'ogType' in c.meta,
        'ogUrl': 'ogUrl' in c.meta,
        'twitterCard': 'twitterCard' in c.meta,
        'jsonLd': bool(c.jsonld),
        'jsonLdBlocks': len(c.jsonld),
        'jsonLdValid': all(valid) if valid else None,
        'robotsMeta': c.meta.get('robotsMeta'),
        'hreflang': c.hreflang,
        'h1': c.headings.count(1),
        'headingSkip': _skips(c.headings),
        'imgWithoutAlt': c.img_without_alt,
        'emptyLinks': c.empty_links,
        'faviconLink': c.favicon_link,
    }
    s['present'] = sum(1 for k in PAGE_SIGNALS if s[k] not in (False, None, ''))
    return s


def _sitemap(site_dir):
    path = os.path.join(site_dir, 'sitemap.xml')
    if not os.path.isfile(path):
        return {'present': False, 'valid': None, 'urls': None}
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return {'present': True, 'valid': False, 'urls': None}
    if not root.tag.endswith(('urlset', 'sitemapindex')):
        return {'present': True, 'valid': False, 'urls': None}
    return {'present': True, 'valid': True,
            'urls': sum(1 for el in root.iter() if el.tag.endswith('loc'))}


def site_signals(site_dir, page_signals_list):
    exists = lambda rel: os.path.isfile(os.path.join(site_dir, rel))  # noqa: E731
    return {
        'robotsTxt': exists('robots.txt'),
        'sitemap': _sitemap(site_dir),
        'feed': any(exists(f) for f in FEEDS),
        'favicon': any(exists(f) for f in FAVICONS)
        or any(s.get('faviconLink') for s in page_signals_list),
    }


def seo_section(site_dir, pages):
    signals = {key: page_signals(site._read(os.path.join(site_dir, page['file'])))
               for key, page in pages.items()}
    return {
        'total': len(PAGE_SIGNALS),
        'pages': signals,
        'present': {key: s['present'] for key, s in signals.items()},
        'site': site_signals(site_dir, list(signals.values())),
    }
```

- [ ] **Step 4: Run the tests**

Run: `python3 -m pytest -q tests/test_quality_seo.py && ruff check toolset tests`
Expected: all pass. If ruff flags E731 despite the `noqa`, turn `exists` into a nested `def`.

- [ ] **Step 5: Commit**

```bash
git add toolset/quality/seo.py tests/test_quality_seo.py
git commit -m "feat(quality): SEO signals per page and site (spec 009 R-9)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Reduce the collector output (`toolset/quality/reduce.py`)

**Files:**
- Create: `toolset/quality/reduce.py`
- Create: `tests/fixtures/quality/raw.json` (a full collector output for the fixture site)
- Test: `tests/test_quality_reduce.py`

**Interfaces:**
- Consumes:
  - `site.extra_output`, `site.works_without_js`, `site.REFERENCE_ASSETS` (Task 1);
  - `seo.seo_section` (Task 2);
  - the `raw.json` contract in `plan.md`.
- Produces:
  - `SECTIONS`, `spread`
  - `reduce_lighthouse`, `reduce_axe`, `reduce_html`, `reduce_links`, `weight`, `js_section`
  - `build_quality(raw, site_dir, pages, output_glob) -> dict` (the `quality.json` contract)

- [ ] **Step 1: Write the raw fixture**

Generate `tests/fixtures/quality/raw.json`, so it matches the fixture site byte for byte:

```bash
python3 - <<'EOF'
import gzip, json, os, pathlib
site = pathlib.Path('tests/fixtures/quality/site')
def run(perf, lcp, failed):
    return {"scores": {"performance": perf, "accessibility": 1, "best-practices": 1, "seo": 0.82},
            "metrics": {"fcp": lcp, "lcp": lcp, "tbt": 0, "cls": 0, "si": lcp},
            "resources": {"totalBytes": 2400, "jsBytes": 0, "cssBytes": 300, "requests": 2, "domSize": 40},
            "failedAudits": failed}
pages = {"index": {"url": "/", "file": "index.html"},
         "post": {"url": "/post/hello/", "file": "post/hello/index.html"},
         "404": {"url": "/404.html", "file": "404.html"}}
lh = {p: [run(0.97, 900, ["a"]), run(0.99, 700, ["c"]), run(0.98, 800, ["b"])] for p in pages}
files = []
for f in sorted(str(p.relative_to(site)).replace(os.sep, '/') for p in site.rglob('*') if p.is_file()):
    data = (site / f).read_bytes()
    files.append({"path": f, "bytes": len(data), "gzip": len(gzip.compress(data, 9)), "br": len(gzip.compress(data, 9)) - 1})
raw = {"tools": {"node": "v24.21.0", "lighthouse": "1.0.0", "playwright": "1.0.0", "chromium": "1.0",
                 "axeCore": "1.0.0", "htmlValidate": "1.0.0", "chromeLauncher": "1.0.0", "lychee": "1.0.0"},
       "pages": pages,
       "lighthouse": {"mobile": lh, "desktop": lh},
       "axe": {"index": {"violations": []},
               "post": {"violations": [{"id": "color-contrast", "impact": "serious", "nodes": 3},
                                       {"id": "region", "impact": "moderate", "nodes": 1}]},
               "404": {"violations": []}},
       "rendered": {"post": {"title": "Hello", "firstParagraph": "First paragraph of the post."}},
       "html": {"index": {"messages": []},
                "post": {"messages": [{"ruleId": "no-inline-style", "severity": 2},
                                      {"ruleId": "prefer-native-element", "severity": 1}]},
                "404": {"messages": []}},
       "links": {"report": {"fail_map": {str(site / "index.html"): [
           {"url": "file:///x/missing.css", "status": {"text": "Cannot find file"}},
           {"url": "file:///x/post/hello/#nope", "status": {"text": "Cannot find fragment"}}]}}},
       "files": files}
pathlib.Path('tests/fixtures/quality/raw.json').write_text(json.dumps(raw, indent=2) + "\n")
EOF
```

- [ ] **Step 2: Write the failing tests**

`tests/test_quality_reduce.py`:

```python
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
```

- [ ] **Step 3: Run them and see them fail**

Run: `python3 -m pytest -q tests/test_quality_reduce.py`
Expected: FAIL with `ImportError: cannot import name 'reduce'`.

- [ ] **Step 4: Implement `toolset/quality/reduce.py`**

```python
'''
Reduces the collector output (quality/run.mjs raw.json) into quality.json
(spec 009 R-8, R-10..R-16). Pure functions; the contracts are in plan.md.
'''
import fnmatch
import posixpath
import statistics

from toolset.quality import seo, site

SECTIONS = ('lighthouse', 'seo', 'html', 'a11y', 'links', 'weight', 'js', 'extra')
PRESETS = ('mobile', 'desktop')
SCORES = ('performance', 'accessibility', 'best-practices', 'seo')
METRICS = ('fcp', 'lcp', 'tbt', 'cls', 'si')
RESOURCES = ('totalBytes', 'jsBytes', 'cssBytes', 'requests', 'domSize')
IMPACTS = ('critical', 'serious', 'moderate', 'minor')
MAX_BROKEN_LISTED = 20


def spread(values):
    vs = [v for v in values if v is not None]
    if not vs:
        return None
    return {'median': statistics.median(vs), 'min': min(vs), 'max': max(vs)}


def _is_error(part):
    return isinstance(part, dict) and 'error' in part


def _error(part):
    return {'status': 'error', 'error': part['error']}


def _median_run(runs):
    ranked = sorted(runs, key=lambda r: (r['scores'].get('performance') is None,
                                         r['scores'].get('performance') or 0))
    return ranked[(len(ranked) - 1) // 2]


def _lighthouse_page(runs):
    if _is_error(runs):
        return _error(runs)
    good = [r for r in runs if not _is_error(r)]
    if not good:
        return {'status': 'error', 'error': runs[0]['error'] if runs else 'no runs'}
    return {
        'status': 'ok',
        'runs': len(good),
        'scores': {k: spread([r['scores'].get(k) for r in good]) for k in SCORES},
        'metrics': {k: spread([r['metrics'].get(k) for r in good]) for k in METRICS},
        'resources': {k: spread([r['resources'].get(k) for r in good]) for k in RESOURCES},
        'failedAudits': _median_run(good)['failedAudits'],
    }


def reduce_lighthouse(raw_lh):
    return {preset: {page: _lighthouse_page(runs)
                     for page, runs in (raw_lh.get(preset) or {}).items()}
            for preset in PRESETS}


def reduce_axe(raw_axe):
    out = {}
    for page, data in raw_axe.items():
        if _is_error(data):
            out[page] = _error(data)
            continue
        counts = {impact: 0 for impact in IMPACTS}
        for v in data.get('violations') or []:
            if v.get('impact') in counts:
                counts[v['impact']] += 1
        out[page] = {'violations': counts, 'total': len(data.get('violations') or []),
                     'rules': sorted({v['id'] for v in data.get('violations') or []})}
    return out


def reduce_html(raw_html):
    out = {}
    for page, data in raw_html.items():
        if _is_error(data):
            out[page] = _error(data)
            continue
        messages = data.get('messages') or []
        out[page] = {'errors': sum(1 for m in messages if m.get('severity') == 2),
                     'warnings': sum(1 for m in messages if m.get('severity') == 1),
                     'rules': sorted({m['ruleId'] for m in messages if m.get('ruleId')})}
    return out


def _kind(url):
    if '#' in url:
        return 'anchor'
    path = url.split('?', 1)[0]
    if path.endswith('/') or path.endswith('.html') or not posixpath.splitext(path)[1]:
        return 'link'
    return 'asset'


def reduce_links(raw_links):
    report = raw_links.get('report') or {}
    fail_map = report.get('fail_map') or report.get('error_map') or {}
    items = []
    for source, failures in sorted(fail_map.items()):
        for f in failures:
            status = f.get('status')
            items.append({'source': source, 'url': f.get('url'),
                          'status': status.get('text') if isinstance(status, dict) else status})
    by_kind = {'link': 0, 'anchor': 0, 'asset': 0}
    for item in items:
        by_kind[_kind(item['url'] or '')] += 1
    return {'broken': len(items), 'byKind': by_kind, 'items': items[:MAX_BROKEN_LISTED]}


def weight(files, output_glob):
    posts = [f['bytes'] for f in files if fnmatch.fnmatch(f['path'], output_glob)]
    total = sum(f['bytes'] for f in files)
    reference = sum(f['bytes'] for f in files if f['path'] in site.REFERENCE_ASSETS)
    return {'bytes': total,
            'gzipBytes': sum(f['gzip'] for f in files),
            'brotliBytes': sum(f['br'] for f in files),
            'bytesPerPost': round(sum(posts) / len(posts)) if posts else None,
            'generatorAddedBytes': total - reference}


def js_section(lighthouse, files, works):
    pages = {}
    for page, data in (lighthouse.get('mobile') or {}).items():
        js = (data.get('resources') or {}).get('jsBytes') if data.get('status') == 'ok' else None
        pages[page] = js['median'] if js else None
    known = [v for v in pages.values() if v is not None]
    js_class = None if not known else ('none' if all(v == 0 for v in known) else 'hydrated')
    return {'pages': pages,
            'diskBytes': sum(f['bytes'] for f in files if f['path'].endswith(('.js', '.mjs'))),
            'jsClass': js_class,
            'worksWithoutJs': works}


def _raw(raw, key):
    part = raw.get(key)
    if part is None:
        raise RuntimeError('%s missing in collector output' % key)
    if _is_error(part):
        raise RuntimeError(part['error'])
    return part


def _section(fn):
    try:
        return dict({'status': 'ok'}, **fn())
    except Exception as e:
        return {'status': 'error', 'error': '%s: %s' % (type(e).__name__, e)}


def build_quality(raw, site_dir, pages, output_glob):
    '''quality.json (R-16): one section per check, each ok or error.'''
    q = {'status': 'ok', 'pages': {k: v['url'] for k, v in pages.items()},
         'tools': raw.get('tools')}
    q['lighthouse'] = _section(lambda: reduce_lighthouse(_raw(raw, 'lighthouse')))
    q['seo'] = _section(lambda: seo.seo_section(site_dir, pages))
    q['html'] = _section(lambda: {'pages': reduce_html(_raw(raw, 'html'))})
    q['a11y'] = _section(lambda: {'pages': reduce_axe(_raw(raw, 'axe'))})
    q['links'] = _section(lambda: reduce_links(_raw(raw, 'links')))
    q['weight'] = _section(lambda: weight(_raw(raw, 'files'), output_glob))

    def js():
        if q['lighthouse']['status'] != 'ok':
            raise RuntimeError('lighthouse section failed')
        rendered = (raw.get('rendered') or {}).get('post') if not _is_error(raw.get('rendered')) else None
        works = site.works_without_js(site_dir, pages['post']['file'], rendered)
        return js_section(q['lighthouse'], _raw(raw, 'files'), works)

    q['js'] = _section(js)
    q['extra'] = _section(lambda: site.extra_output(site_dir, output_glob))
    return q
```

- [ ] **Step 5: Run the tests**

Run: `python3 -m pytest -q tests/test_quality_reduce.py && ruff check toolset tests`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add toolset/quality/reduce.py tests/test_quality_reduce.py tests/fixtures/quality/raw.json
git commit -m "feat(quality): reduce collector output into quality.json (spec 009)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Collector image (`quality/`)

**Files:**
- Create: `quality/Dockerfile`, `quality/package.json`, `quality/package-lock.json`, `quality/run.mjs`, `quality/.dockerignore`
- Create: `quality/test/pages.json`, `quality/test/expected-shape.json`, `quality/test/check-shape.mjs`
- Test: the image itself (Step 7). It needs Docker; take the Docker lock in `/Users/jobs/Dev/ssgberk/.docker-smoke.lock` with `mkdir`/`rmdir` if working on the shared machine, and check for ≥5 GiB free disk first.

**Interfaces:**
- Consumes: the fixture site (Task 1).
- Produces: the image `ssgberk/quality` and the collector CLI and `raw.json` contracts in `plan.md`.

- [ ] **Step 1: Pin the versions**

Resolve the latest stable versions, and record them in the commit message:

```bash
for p in lighthouse chrome-launcher playwright axe-core html-validate; do echo "$p $(npm view $p version)"; done
gh release view --repo lycheeverse/lychee --json tagName,assets --jq '.tagName, [.assets[].name]'
```

`quality/package.json` (replace each `X.Y.Z` with the resolved version, exact, no `^`):

```json
{
  "name": "ssgberk-quality",
  "private": true,
  "type": "module",
  "description": "SSGBerk output quality collector (benchmark-tool spec 009)",
  "dependencies": {
    "axe-core": "X.Y.Z",
    "chrome-launcher": "X.Y.Z",
    "html-validate": "X.Y.Z",
    "lighthouse": "X.Y.Z",
    "playwright": "X.Y.Z"
  }
}
```

Then generate the lock: `cd quality && npm install --package-lock-only --ignore-scripts && cd ..`. If `npm` is not on the host, run the same command in `docker run --rm -v "$PWD/quality:/q" -w /q node:24 ...`.

`quality/.dockerignore`:

```
node_modules
test
```

- [ ] **Step 2: Write `quality/Dockerfile`**

Set `LYCHEE_VERSION` to the resolved release tag without the `lychee-v` or `v` prefix. Check that the asset names match `lychee-<arch>-unknown-linux-gnu.tar.gz`, and adjust the URL if the release uses another name.

```dockerfile
# SSGBerk quality collector (benchmark-tool spec 009): Lighthouse, axe-core,
# html-validate and lychee against Playwright's Chromium. Runs with no network.
FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=24.21.0
ARG LYCHEE_VERSION=X.Y.Z

RUN apt-get -yqq update \
 && apt-get -yqq install --no-install-recommends ca-certificates curl xz-utils \
 && rm -rf /var/lib/apt/lists/*

RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in amd64) NARCH=x64 ;; arm64) NARCH=arm64 ;; *) echo "unsupported $ARCH"; exit 1 ;; esac \
 && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NARCH}.tar.xz" \
    | tar -xJ -C /usr/local --strip-components=1 \
 && node --version

RUN ARCH="$(dpkg --print-architecture)" \
 && case "$ARCH" in amd64) LARCH=x86_64 ;; arm64) LARCH=aarch64 ;; *) echo "unsupported $ARCH"; exit 1 ;; esac \
 && curl -fsSL "https://github.com/lycheeverse/lychee/releases/download/lychee-v${LYCHEE_VERSION}/lychee-${LARCH}-unknown-linux-gnu.tar.gz" \
    | tar -xz -C /usr/local/bin lychee \
 && lychee --version

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright NPM_CONFIG_UPDATE_NOTIFIER=false
WORKDIR /quality
COPY package.json package-lock.json ./
RUN npm ci --omit=dev \
 && npx playwright install --with-deps chromium \
 && rm -rf /root/.npm /var/lib/apt/lists/*
COPY run.mjs ./
RUN mkdir -p /work/out
WORKDIR /work
```

- [ ] **Step 3: Write `quality/run.mjs`**

```js
// SSGBerk quality collector (benchmark-tool spec 009). Writes raw data only:
// toolset/quality/reduce.py turns raw.json into quality.json.
import { execFile } from 'node:child_process';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs, promisify } from 'node:util';
import zlib from 'node:zlib';

import * as chromeLauncher from 'chrome-launcher';
import { HtmlValidate } from 'html-validate';
import lighthouse from 'lighthouse';
import desktopConfig from 'lighthouse/core/config/desktop-config.js';
import { chromium } from 'playwright';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const RUNS = 3;
const PRESETS = { mobile: undefined, desktop: desktopConfig };
const CATEGORIES = ['performance', 'accessibility', 'best-practices', 'seo'];
const CHROME_FLAGS = ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'];
const NOT_SCORED = new Set(['informative', 'manual', 'notApplicable', 'error']);
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.gif': 'image/gif', '.ico': 'image/x-icon', '.woff': 'font/woff',
  '.woff2': 'font/woff2', '.wasm': 'application/wasm',
};
const COMPRESSIBLE = /^(text\/|application\/(json|xml|wasm)|image\/svg\+xml)/;
const execFileP = promisify(execFile);

async function guard(fn) {
  try {
    return await fn();
  } catch (e) {
    return { error: String(e && e.message ? e.message : e) };
  }
}

async function isFile(p) {
  try {
    return (await fs.stat(p)).isFile();
  } catch {
    return false;
  }
}

async function resolveFile(root, pathname) {
  const rel = decodeURIComponent(pathname).replace(/^\/+/, '');
  const base = path.resolve(root, rel);
  if (base !== root && !base.startsWith(root + path.sep)) return null;
  const candidates = rel === '' || rel.endsWith('/')
    ? [path.join(base, 'index.html')]
    : [base, path.join(base, 'index.html'), `${base}.html`];
  for (const c of candidates) if (await isFile(c)) return c;
  return null;
}

// Fixed static server: gzip, no-cache, directory index, 404.html with status 404.
function serve(root) {
  const server = http.createServer(async (req, res) => {
    const { pathname } = new URL(req.url, 'http://127.0.0.1');
    let file = await resolveFile(root, pathname);
    let status = 200;
    if (!file) {
      status = 404;
      file = (await isFile(path.join(root, '404.html'))) ? path.join(root, '404.html') : null;
    }
    let body = file ? await fs.readFile(file) : Buffer.from('Not found');
    const type = file ? TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream'
      : 'text/plain; charset=utf-8';
    const headers = { 'content-type': type, 'cache-control': 'no-cache' };
    if (COMPRESSIBLE.test(type) && /\bgzip\b/.test(req.headers['accept-encoding'] || '')) {
      body = zlib.gzipSync(body);
      headers['content-encoding'] = 'gzip';
      headers.vary = 'accept-encoding';
    }
    headers['content-length'] = body.length;
    res.writeHead(status, headers);
    res.end(req.method === 'HEAD' ? undefined : body);
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({
    server, origin: `http://127.0.0.1:${server.address().port}`,
  })));
}

function summarize(lhr) {
  const audits = lhr.audits;
  const value = (id) => audits[id]?.numericValue ?? null;
  const requests = audits['network-requests']?.details?.items ?? [];
  const bytes = (type) => requests.filter((r) => r.resourceType === type)
    .reduce((sum, r) => sum + (r.transferSize || 0), 0);
  return {
    scores: Object.fromEntries(CATEGORIES.map((c) => [c, lhr.categories[c]?.score ?? null])),
    metrics: {
      fcp: value('first-contentful-paint'),
      lcp: value('largest-contentful-paint'),
      tbt: value('total-blocking-time'),
      cls: value('cumulative-layout-shift'),
      si: value('speed-index'),
    },
    resources: {
      totalBytes: value('total-byte-weight'),
      jsBytes: bytes('Script'),
      cssBytes: bytes('Stylesheet'),
      requests: requests.length,
      domSize: value('dom-size') ?? value('dom-size-insight'),
    },
    failedAudits: Object.values(audits)
      .filter((a) => !NOT_SCORED.has(a.scoreDisplayMode) && a.score !== null && a.score < 1)
      .map((a) => a.id).sort(),
  };
}

async function runLighthouse(origin, pages) {
  const chrome = await chromeLauncher.launch({
    chromePath: chromium.executablePath(), chromeFlags: CHROME_FLAGS,
  });
  try {
    const out = {};
    for (const [preset, config] of Object.entries(PRESETS)) {
      out[preset] = {};
      for (const [key, page] of Object.entries(pages)) {
        const runs = [];
        for (let i = 0; i < RUNS; i += 1) {
          runs.push(await guard(async () => {
            const result = await lighthouse(origin + page.url, {
              port: chrome.port, output: 'json', logLevel: 'error', onlyCategories: CATEGORIES,
            }, config);
            if (!result?.lhr) throw new Error('lighthouse returned no report');
            if (result.lhr.runtimeError) throw new Error(result.lhr.runtimeError.message);
            return summarize(result.lhr);
          }));
        }
        out[preset][key] = runs;
      }
    }
    return out;
  } finally {
    await chrome.kill();
  }
}

async function runBrowserChecks(origin, pages) {
  const axeSource = await fs.readFile(path.join(HERE, 'node_modules', 'axe-core', 'axe.min.js'), 'utf8');
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  try {
    const axe = {};
    for (const [key, page] of Object.entries(pages)) {
      axe[key] = await guard(async () => {
        const tab = await browser.newPage();
        try {
          await tab.goto(origin + page.url, { waitUntil: 'load' });
          await tab.addScriptTag({ content: axeSource });
          const result = await tab.evaluate(() => window.axe.run(document, { resultTypes: ['violations'] }));
          return {
            violations: result.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length })),
          };
        } finally {
          await tab.close();
        }
      });
    }
    const post = await guard(async () => {
      const tab = await browser.newPage();
      try {
        await tab.goto(origin + pages.post.url, { waitUntil: 'networkidle' });
        const text = async (selector) => ((await tab.locator(selector).first()
          .textContent({ timeout: 5000 })) || '').trim();
        return { title: await text('h1.post-title'), firstParagraph: await text('.post-body p') };
      } finally {
        await tab.close();
      }
    });
    return { axe, rendered: { post }, chromium: browser.version() };
  } finally {
    await browser.close();
  }
}

async function runHtmlValidate(site, pages) {
  const validator = new HtmlValidate({ extends: ['html-validate:recommended'] });
  const out = {};
  for (const [key, page] of Object.entries(pages)) {
    out[key] = await guard(async () => {
      const report = await validator.validateFile(path.join(site, page.file));
      return {
        messages: report.results.flatMap((r) => r.messages)
          .map((m) => ({ ruleId: m.ruleId, severity: m.severity })),
      };
    });
  }
  return out;
}

async function runLychee(site, outDir) {
  const report = path.join(outDir, 'lychee.json');
  try {
    await execFileP('lychee', ['--offline', '--no-progress', '--include-fragments', '--format', 'json',
      '--output', report, '--root-dir', site, site], { maxBuffer: 64 * 1024 * 1024 });
  } catch (e) {
    // exit code 2 means broken links; the report is still written
    if (!(await isFile(report))) throw e;
  }
  return { report: JSON.parse(await fs.readFile(report, 'utf8')) };
}

async function listFiles(dir) {
  const out = [];
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await listFiles(full));
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

async function sizes(site) {
  const files = [];
  for (const full of (await listFiles(site)).sort()) {
    const data = await fs.readFile(full);
    files.push({
      path: path.relative(site, full).split(path.sep).join('/'),
      bytes: data.length,
      gzip: zlib.gzipSync(data, { level: 9 }).length,
      br: zlib.brotliCompressSync(data, {
        params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 },
      }).length,
    });
  }
  return files;
}

async function packageVersion(name) {
  const file = path.join(HERE, 'node_modules', name, 'package.json');
  return JSON.parse(await fs.readFile(file, 'utf8')).version;
}

async function tools(chromiumVersion) {
  const lychee = await guard(async () => (await execFileP('lychee', ['--version'])).stdout.trim()
    .split(/\s+/).pop());
  return {
    node: process.version,
    lighthouse: await packageVersion('lighthouse'),
    playwright: await packageVersion('playwright'),
    chromium: chromiumVersion ?? null,
    axeCore: await packageVersion('axe-core'),
    htmlValidate: await packageVersion('html-validate'),
    chromeLauncher: await packageVersion('chrome-launcher'),
    lychee: typeof lychee === 'string' ? lychee : null,
  };
}

async function main() {
  const { values } = parseArgs({
    options: { site: { type: 'string' }, pages: { type: 'string' }, out: { type: 'string' } },
  });
  const site = path.resolve(values.site);
  const pages = JSON.parse(values.pages);
  const outDir = path.resolve(values.out);
  await fs.mkdir(outDir, { recursive: true });
  const raw = { pages };
  const { server, origin } = await serve(site);
  try {
    const browser = await guard(() => runBrowserChecks(origin, pages));
    raw.axe = browser.error ? browser : browser.axe;
    raw.rendered = browser.error ? browser : browser.rendered;
    raw.lighthouse = await guard(() => runLighthouse(origin, pages));
    raw.html = await guard(() => runHtmlValidate(site, pages));
    raw.links = await guard(() => runLychee(site, outDir));
    raw.files = await guard(() => sizes(site));
    raw.tools = await guard(() => tools(browser.chromium));
  } finally {
    server.close();
  }
  await fs.writeFile(path.join(outDir, 'raw.json'), JSON.stringify(raw, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
```

- [ ] **Step 4: Write the collector test files**

`quality/test/pages.json`:

```json
{"index": {"url": "/", "file": "index.html"}, "post": {"url": "/post/hello/", "file": "post/hello/index.html"}, "404": {"url": "/404.html", "file": "404.html"}}
```

`quality/test/expected-shape.json`. A string is a type (`"a|b"` allows either), an object is checked key by key, and a one-element array means every element must match that element:

```json
{
  "tools": {"node": "string", "lighthouse": "string", "playwright": "string", "chromium": "string",
            "axeCore": "string", "htmlValidate": "string", "chromeLauncher": "string", "lychee": "string"},
  "pages": "object",
  "lighthouse": {
    "mobile": {
      "index": [{"scores": {"performance": "number", "accessibility": "number", "best-practices": "number", "seo": "number"},
                 "metrics": {"fcp": "number", "lcp": "number", "tbt": "number", "cls": "number", "si": "number"},
                 "resources": {"totalBytes": "number", "jsBytes": "number", "cssBytes": "number", "requests": "number", "domSize": "number|null"},
                 "failedAudits": "array"}],
      "post": [{"scores": {"performance": "number", "accessibility": "number", "best-practices": "number", "seo": "number"},
                "metrics": {"fcp": "number", "lcp": "number", "tbt": "number", "cls": "number", "si": "number"},
                "resources": {"totalBytes": "number", "jsBytes": "number", "cssBytes": "number", "requests": "number", "domSize": "number|null"},
                "failedAudits": "array"}],
      "404": [{"scores": {"performance": "number", "accessibility": "number", "best-practices": "number", "seo": "number"},
               "metrics": {"fcp": "number", "lcp": "number", "tbt": "number", "cls": "number", "si": "number"},
               "resources": {"totalBytes": "number", "jsBytes": "number", "cssBytes": "number", "requests": "number", "domSize": "number|null"},
               "failedAudits": "array"}]
    },
    "desktop": {
      "index": [{"scores": {"performance": "number", "accessibility": "number", "best-practices": "number", "seo": "number"},
                 "metrics": {"fcp": "number", "lcp": "number", "tbt": "number", "cls": "number", "si": "number"},
                 "resources": {"totalBytes": "number", "jsBytes": "number", "cssBytes": "number", "requests": "number", "domSize": "number|null"},
                 "failedAudits": "array"}],
      "post": [{"scores": {"performance": "number", "accessibility": "number", "best-practices": "number", "seo": "number"},
                "metrics": {"fcp": "number", "lcp": "number", "tbt": "number", "cls": "number", "si": "number"},
                "resources": {"totalBytes": "number", "jsBytes": "number", "cssBytes": "number", "requests": "number", "domSize": "number|null"},
                "failedAudits": "array"}],
      "404": [{"scores": {"performance": "number", "accessibility": "number", "best-practices": "number", "seo": "number"},
               "metrics": {"fcp": "number", "lcp": "number", "tbt": "number", "cls": "number", "si": "number"},
               "resources": {"totalBytes": "number", "jsBytes": "number", "cssBytes": "number", "requests": "number", "domSize": "number|null"},
               "failedAudits": "array"}]
    }
  },
  "axe": {"index": {"violations": "array"}, "post": {"violations": "array"}, "404": {"violations": "array"}},
  "rendered": {"post": {"title": "string", "firstParagraph": "string"}},
  "html": {"index": {"messages": "array"}, "post": {"messages": "array"}, "404": {"messages": "array"}},
  "links": {"report": "object"},
  "files": [{"path": "string", "bytes": "number", "gzip": "number", "br": "number"}]
}
```

`quality/test/check-shape.mjs`:

```js
// Checks a collector raw.json against expected-shape.json (keys and types, not values).
import fs from 'node:fs';

const [rawPath, shapePath] = process.argv.slice(2);
const raw = JSON.parse(fs.readFileSync(rawPath, 'utf8'));
const shape = JSON.parse(fs.readFileSync(shapePath, 'utf8'));
const errors = [];

function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

function check(value, expected, where) {
  if (typeof expected === 'string') {
    if (!expected.split('|').includes(typeOf(value))) errors.push(`${where}: ${typeOf(value)} is not ${expected}`);
  } else if (Array.isArray(expected)) {
    if (!Array.isArray(value) || value.length === 0) errors.push(`${where}: expected a non-empty array`);
    else value.forEach((v, i) => check(v, expected[0], `${where}[${i}]`));
  } else {
    if (typeOf(value) !== 'object') {
      errors.push(`${where}: expected an object, got ${JSON.stringify(value).slice(0, 200)}`);
      return;
    }
    for (const [k, e] of Object.entries(expected)) check(value[k], e, `${where}.${k}`);
  }
}

check(raw, shape, 'raw');
for (const preset of ['mobile', 'desktop']) {
  for (const page of ['index', 'post', '404']) {
    if ((raw.lighthouse?.[preset]?.[page] || []).length !== 3) errors.push(`lighthouse.${preset}.${page}: expected 3 runs`);
  }
}
if (raw.rendered?.post?.title !== 'Hello') errors.push('rendered.post.title is not "Hello"');
if (raw.lighthouse?.mobile?.post?.[0]?.resources?.jsBytes !== 0) errors.push('fixture post page should request 0 JS bytes');
if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log('raw.json shape ok');
```

- [ ] **Step 5: Build the image**

Run: `docker build -t ssgberk/quality quality`
Expected: the build succeeds, and both `node --version` and `lychee --version` print.

- [ ] **Step 6: Run the collector on the fixture and check the shape**

```bash
docker run --rm --network none \
  -v "$PWD/tests/fixtures/quality/site:/fixture:ro" -v "$PWD/quality/test:/test:ro" \
  ssgberk/quality sh -c 'node /quality/run.mjs --site /fixture --pages "$(cat /test/pages.json)" --out /tmp/out \
    && node /test/check-shape.mjs /tmp/out/raw.json /test/expected-shape.json'
```

Expected: `raw.json shape ok`. If a check fails because the pinned version renamed something (a Lighthouse audit id such as `network-requests` or `dom-size`, a lychee flag or its JSON keys, or the `html-validate` API), fix `run.mjs` for the pinned version. If the lychee JSON uses keys other than `fail_map` or `error_map`, update `reduce.reduce_links` and the `links` part of `tests/fixtures/quality/raw.json` to match. Re-run until it passes. Keep the fixture site unchanged.

- [ ] **Step 7: Remove the local image and commit**

```bash
docker rmi ssgberk/quality
git add quality
git commit -m "feat(quality): pinned collector image with Lighthouse, axe-core, html-validate, lychee (spec 009 R-4, R-5)

Pinned: lighthouse X, chrome-launcher X, playwright X (Chromium X), axe-core X,
html-validate X, lychee X, Node 24.21.0.

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Docker plumbing (`toolset/utils/docker_helper.py`)

**Files:**
- Modify: `toolset/utils/docker_helper.py`
  - imports at the top: `io`, `json`, `posixpath`, `tarfile`;
  - class attributes next to `last_build`;
  - `benchmark()` (signature and the end of its `try` block);
  - new methods after `benchmark()`.
- Test: `tests/test_quality_docker.py`

**Interfaces:**
- Consumes: nothing from earlier tasks (pure Docker plumbing).
- Produces:
  - `QUALITY_IMAGE`, `QUALITY_TIMEOUT_SECONDS`
  - `DockerHelper.benchmark(framework_test, script, variables, raw_file, resources, timeout_seconds, export=None)`
  - `DockerHelper.build_quality_image() -> str`
  - `DockerHelper.run_quality(tar_path, site_name, pages, timeout_seconds=QUALITY_TIMEOUT_SECONDS) -> dict`

- [ ] **Step 1: Write the failing tests**

`tests/test_quality_docker.py`:

```python
import io
import json
import tarfile
import types
from unittest import mock

import docker
import pytest

from toolset.utils import docker_helper

RES = {"cpus": 4.0, "memoryBytes": 8589934592, "swap": False, "cpuset": "4-7"}


def _helper():
    helper = docker_helper.DockerHelper.__new__(docker_helper.DockerHelper)
    helper.benchmarker = mock.Mock()
    helper.server = mock.Mock()
    return helper


def _container(exit_code=0, oom=False):
    c = mock.Mock()
    c.logs.return_value = iter(())
    c.wait.return_value = {"StatusCode": exit_code}
    c.attrs = {"State": {"OOMKilled": oom, "ExitCode": exit_code},
               "Config": {"WorkingDir": "/opt/hugo/src"}}
    c.get_archive.return_value = (iter([b"tar", b"bytes"]), {})
    return c


def test_benchmark_exports_output_on_success(tmp_path):
    helper, c = _helper(), _container()
    helper.server.containers.run.return_value = c
    dest = tmp_path / "quality" / "hugo" / "site.tar"
    out = helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"),
                           RES, 60, export=("public", str(dest)))
    assert out["status"] == "ok"
    c.get_archive.assert_called_once_with("/opt/hugo/src/public")
    assert dest.read_bytes() == b"tarbytes"
    c.remove.assert_called_once_with(force=True)


@pytest.mark.parametrize("exit_code,oom", [(1, False), (137, True)])
def test_benchmark_no_export_on_failure(tmp_path, exit_code, oom):
    helper, c = _helper(), _container(exit_code, oom)
    helper.server.containers.run.return_value = c
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"),
                     RES, 60, export=("public", str(tmp_path / "site.tar")))
    c.get_archive.assert_not_called()


def test_benchmark_export_error_keeps_status(tmp_path):
    helper, c = _helper(), _container()
    c.get_archive.side_effect = docker.errors.NotFound("no such path")
    helper.server.containers.run.return_value = c
    out = helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"),
                           RES, 60, export=("public", str(tmp_path / "site.tar")))
    assert out == {"status": "ok", "exitCode": 0}


def test_benchmark_without_export_never_reads_archive(tmp_path):
    helper, c = _helper(), _container()
    helper.server.containers.run.return_value = c
    helper.benchmark(types.SimpleNamespace(name="hugo"), "build.sh", {}, str(tmp_path / "raw.txt"), RES, 60)
    c.get_archive.assert_not_called()


def _raw_tar(payload):
    buf = io.BytesIO()
    data = json.dumps(payload).encode()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo("raw.json")
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_run_quality_isolated_and_cleaned_up(tmp_path):
    helper = _helper()
    helper._quality_image = "sha256:q"
    c = mock.Mock()
    c.wait.return_value = {"StatusCode": 0}
    c.logs.return_value = b""
    c.get_archive.return_value = (iter([_raw_tar({"tools": {"node": "v24"}})]), {})
    helper.server.containers.create.return_value = c
    tar_path = tmp_path / "site.tar"
    tar_path.write_bytes(b"site-tar")
    pages = {"index": {"url": "/", "file": "index.html"}}
    raw = helper.run_quality(str(tar_path), "public", pages)
    assert raw == {"tools": {"node": "v24"}}
    args, kwargs = helper.server.containers.create.call_args
    assert args[0] == "sha256:q"
    assert kwargs["network_mode"] == "none"
    assert "volumes" not in kwargs and "mounts" not in kwargs
    assert kwargs["command"][:4] == ["node", "/quality/run.mjs", "--site", "/work/public"]
    assert json.loads(kwargs["command"][kwargs["command"].index("--pages") + 1]) == pages
    c.put_archive.assert_called_once_with("/work", b"site-tar")
    c.get_archive.assert_called_once_with("/work/out/raw.json")
    c.remove.assert_called_once_with(force=True)


def test_run_quality_without_raw_json_raises_and_cleans_up(tmp_path):
    helper = _helper()
    helper._quality_image = "sha256:q"
    c = mock.Mock()
    c.wait.return_value = {"StatusCode": 1}
    c.logs.return_value = b"Error: boom"
    c.get_archive.side_effect = docker.errors.NotFound("missing")
    helper.server.containers.create.return_value = c
    (tmp_path / "site.tar").write_bytes(b"x")
    with pytest.raises(RuntimeError, match="exit 1.*boom"):
        helper.run_quality(str(tmp_path / "site.tar"), "public", {})
    c.remove.assert_called_once_with(force=True)


def test_build_quality_image_once(monkeypatch, tmp_path):
    builds = []

    class FakeAPIClient:
        def __init__(self, base_url=None):
            pass

        def build(self, **kw):
            builds.append(kw)
            return iter([{"stream": "Step 1/2 : FROM ubuntu:24.04\n"}, {"stream": "Successfully built abc\n"}])

    monkeypatch.setattr(docker_helper.docker, "APIClient", FakeAPIClient)
    helper = _helper()
    helper._quality_image = None
    helper.benchmarker.config = types.SimpleNamespace(fw_root=str(tmp_path), server_docker_host=None)
    helper.server.images.get.return_value = types.SimpleNamespace(id="sha256:abc")
    assert helper.build_quality_image() == "sha256:abc"
    assert helper.build_quality_image() == "sha256:abc"
    assert len(builds) == 1
    assert builds[0]["path"] == str(tmp_path / "quality") and builds[0]["tag"] == docker_helper.QUALITY_IMAGE


def test_build_quality_image_error(monkeypatch, tmp_path):
    class FakeAPIClient:
        def __init__(self, base_url=None):
            pass

        def build(self, **kw):
            return iter([{"errorDetail": {"message": "npm ci failed"}}])

    monkeypatch.setattr(docker_helper.docker, "APIClient", FakeAPIClient)
    helper = _helper()
    helper._quality_image = None
    helper.benchmarker.config = types.SimpleNamespace(fw_root=str(tmp_path), server_docker_host=None)
    with pytest.raises(RuntimeError, match="npm ci failed"):
        helper.build_quality_image()
```

- [ ] **Step 2: Run them and see them fail**

Run: `python3 -m pytest -q tests/test_quality_docker.py`
Expected: FAIL with `TypeError: ... unexpected keyword argument 'export'` and `AttributeError: ... run_quality`.

- [ ] **Step 3: Implement the changes**

At the top of `toolset/utils/docker_helper.py`, add `import io`, `import json`, `import posixpath` and `import tarfile` with the other stdlib imports. Next to `RUN_LABEL`, add:

```python
QUALITY_IMAGE = 'ssgberk/quality'
QUALITY_TIMEOUT_SECONDS = 1800
QUALITY_MEMORY = '4g'
```

In the class body, next to `last_build = None`, add `_quality_image = None`.

Change the signature of `benchmark` to:

```python
    def benchmark(self, framework_test, script, variables, raw_file,
                  resources, timeout_seconds, export=None):
        '''
        Runs the generator container with fixed resource limits and returns
        {"status": "ok"|"timeout"|"oom", "exitCode": int}. The container is
        always stopped and removed before returning. With export
        (output_folder, dest_tar), a successful build's output is copied to
        dest_tar first (spec 009 R-3).
        '''
```

At the end of its `try:` block, right after the OOM check and before `finally:`, insert:

```python
            if export and status == 'ok' and exit_code == 0:
                DockerHelper.__export_output(container, *export)
```

Add these methods after `benchmark`:

```python
    @staticmethod
    def __export_output(container, output_folder, dest):
        '''Copies <WorkingDir>/<output_folder> to dest as a tar. Never raises.'''
        try:
            workdir = (container.attrs.get('Config') or {}).get('WorkingDir') or '/'
            bits, _ = container.get_archive(posixpath.join(workdir, output_folder))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, 'wb') as f:
                for chunk in bits:
                    f.write(chunk)
        except Exception as e:
            log("quality: could not export %s: %s" % (output_folder, e), color=Fore.YELLOW)

    def build_quality_image(self):
        '''
        Builds ssgberk/quality from <fw_root>/quality once per process
        (spec 009 R-4), outside the generator build-time accounting.
        '''
        if self._quality_image:
            return self._quality_image
        client = docker.APIClient(base_url=self.benchmarker.config.server_docker_host)
        for token in client.build(path=os.path.join(self.benchmarker.config.fw_root, 'quality'),
                                  dockerfile='Dockerfile', tag=QUALITY_IMAGE, forcerm=True,
                                  pull=True, timeout=3600, decode=True):
            if 'errorDetail' in token:
                raise RuntimeError(token['errorDetail']['message'])
            if token.get('stream', '').strip():
                log(token['stream'].rstrip(), prefix='quality: ')
        self._quality_image = self.server.images.get(QUALITY_IMAGE).id
        return self._quality_image

    def run_quality(self, tar_path, site_name, pages,
                    timeout_seconds=QUALITY_TIMEOUT_SECONDS):
        '''
        Runs quality/run.mjs on the exported site with no network and no
        mounts (spec 009 R-4, R-5) and returns its raw.json.
        '''
        image = self.build_quality_image()
        command = ['node', '/quality/run.mjs', '--site', '/work/' + site_name,
                   '--pages', json.dumps(pages), '--out', '/work/out']
        container = self.server.containers.create(
            image, command=command, labels=self._run_labels(), network_mode='none',
            mem_limit=QUALITY_MEMORY, working_dir='/work')
        try:
            with open(tar_path, 'rb') as f:
                container.put_archive('/work', f.read())
            container.start()
            result = container.wait(timeout=timeout_seconds)
            try:
                bits, _ = container.get_archive('/work/out/raw.json')
            except docker.errors.NotFound:
                logs = container.logs().decode('utf-8', 'replace')
                raise RuntimeError('collector wrote no raw.json (exit %s): %s' % (
                    result.get('StatusCode'), logs[-2000:]))
            with tarfile.open(fileobj=io.BytesIO(b''.join(bits))) as tar:
                return json.load(tar.extractfile(tar.getmembers()[0]))
        finally:
            try:
                container.remove(force=True)
            except docker.errors.NotFound:
                pass
```

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest -q && ruff check toolset tests`
Expected: all pass, including the existing `tests/test_docker_helper.py`.

- [ ] **Step 5: Commit**

```bash
git add toolset/utils/docker_helper.py tests/test_quality_docker.py
git commit -m "feat(quality): export build output and run the collector without network (spec 009 R-3..R-5)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: The pass in a run (runner, CLI, Benchmarker, Results)

**Files:**
- Create: `toolset/quality/runner.py`
- Modify:
  - `toolset/run-tests.py`: a new `--quality` argument after `--no-cache`;
  - `toolset/utils/benchmark_config.py`: `self.quality` next to `self.no_cache`;
  - `toolset/benchmark/benchmarker.py`: `benchmark_type` in `__benchmark`, `__noise_control`, and two new private methods;
  - `toolset/utils/results.py`: `STORED_RUN_KEYS`, `__init__`, `add_quality`, `__to_jsonable`, `write_summary`.
- Test: `tests/test_quality_runner.py`

**Interfaces:**
- Consumes:
  - `site.generator_config`, `site.extract`, `site.resolve_pages` (Task 1);
  - `reduce.build_quality` (Task 3);
  - `DockerHelper.run_quality`, `DockerHelper.benchmark(..., export=...)`, `DockerHelper._quality_image` (Task 5).
- Produces:
  - `runner.eligible(config)`, `runner.skipped(config)`, `runner.archive_path(results_dir, name)`, `runner.run_pass(docker_helper, test, results_dir)`
  - `Results.add_quality(name, quality, image_id=None)`
  - `results.json` `quality` and `environment.quality`
  - `config.quality`

- [ ] **Step 1: Write the failing tests**

`tests/test_quality_runner.py`:

```python
import json
import pathlib
import tarfile
import types
from unittest import mock

from toolset.quality import runner
from toolset.utils.results import STORED_RUN_KEYS, Results

FIX = pathlib.Path(__file__).parent / "fixtures" / "quality"


def _cfg(**kw):
    return types.SimpleNamespace(**kw)


def test_eligible_and_skipped():
    assert not runner.eligible(_cfg())
    assert not runner.skipped(_cfg())
    assert runner.eligible(_cfg(quality=True, suite_info=None, number_of_files="10", content_size="0.500"))
    p0 = _cfg(quality=True, suite_info={"name": "P"}, number_of_files="50", content_size="5")
    p1 = _cfg(quality=True, suite_info={"name": "P"}, number_of_files="50", content_size="50")
    assert runner.eligible(p0) and not runner.skipped(p0)
    assert not runner.eligible(p1) and runner.skipped(p1)


def _generator(tmp_path):
    d = tmp_path / "frameworks" / "Go" / "hugo"
    d.mkdir(parents=True)
    (d / "benchmark_config.json").write_text(json.dumps(
        {"framework": "hugo", "config": [{"output_folder": "public", "output_glob": "post/*/index.html"}]}))
    return types.SimpleNamespace(name="hugo", directory=str(d))


def _archive(results_dir):
    tar_path = pathlib.Path(runner.archive_path(str(results_dir), "hugo"))
    tar_path.parent.mkdir(parents=True)
    with tarfile.open(tar_path, "w") as tar:
        tar.add(FIX / "site", arcname="public")
    return tar_path


def test_run_pass_ok(tmp_path):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    tar_path = _archive(results_dir)
    helper = mock.Mock()
    helper.run_quality.return_value = json.loads((FIX / "raw.json").read_text())
    q = runner.run_pass(helper, test, str(results_dir))
    assert q["status"] == "ok" and q["lighthouse"]["status"] == "ok"
    args = helper.run_quality.call_args[0]
    assert args[0] == str(tar_path) and args[1] == "public"
    assert args[2]["post"] == {"url": "/post/hello/", "file": "post/hello/index.html"}
    out = results_dir / "quality" / "hugo"
    assert json.loads((out / "quality.json").read_text()) == q
    assert (out / "raw.json").exists() and (out / "site" / "index.html").exists()
    assert not tar_path.exists()


def test_run_pass_missing_archive(tmp_path):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    q = runner.run_pass(mock.Mock(), test, str(results_dir))
    assert q["status"] == "error" and "no exported output" in q["error"]
    assert json.loads((results_dir / "quality" / "hugo" / "quality.json").read_text()) == q


def test_run_pass_collector_error(tmp_path):
    test, results_dir = _generator(tmp_path), tmp_path / "results"
    _archive(results_dir)
    helper = mock.Mock()
    helper.run_quality.side_effect = RuntimeError("collector wrote no raw.json (exit 1)")
    q = runner.run_pass(helper, test, str(results_dir))
    assert q == {"status": "error", "error": "RuntimeError: collector wrote no raw.json (exit 1)"}


def _bm(tmp_path, quality=True, results=None, failure=None):
    from toolset.benchmark.benchmarker import Benchmarker
    tmp_path.mkdir(parents=True, exist_ok=True)
    b = Benchmarker.__new__(Benchmarker)
    b.config = types.SimpleNamespace(min_runs="1", run_test_timeout_seconds=10, resources={"cpus": 1},
                                     quality=quality, suite_info=None, number_of_files="50",
                                     content_size="5")
    test_type = mock.Mock()
    test_type.get_script_name.return_value = "build.sh"
    test_type.get_script_variables.return_value = {"min_runs": "1"}
    b.config.types = {"datarate": test_type}
    b.results = mock.Mock()
    b.results.directory = str(tmp_path / "results")
    b.results.get_raw_file.return_value = str(tmp_path / "raw.txt")
    exports = []

    def bench(ft, script, variables, raw_file, res, timeout, export=None):
        exports.append(export)
        return {"status": "ok", "exitCode": 0}

    b.docker_helper = mock.Mock()
    b.docker_helper.benchmark.side_effect = bench
    b.docker_helper._quality_image = "sha256:q"
    b.results.parse_test.return_value = {
        "results": [{"cv": None, "median": 1.0}] if results is None else results,
        "status": "ok", "failureReason": failure, "unsupported": False}
    b._Benchmarker__begin_logging = mock.Mock()
    b._Benchmarker__end_logging = mock.Mock()
    ft = _generator(tmp_path)
    ft.runTests = {"datarate": mock.Mock(failed=False)}
    return b, ft, exports


def test_quality_pass_runs_after_ok(tmp_path, monkeypatch):
    b, ft, exports = _bm(tmp_path)
    monkeypatch.setattr(runner, "run_pass", lambda helper, test, d: {"status": "ok", "test": test.name})
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert exports == [("public", runner.archive_path(b.results.directory, "hugo"))]
    b.results.add_quality.assert_called_once_with("hugo", {"status": "ok", "test": "hugo"}, "sha256:q")


def test_quality_pass_missing_archive_keeps_result(tmp_path):
    reported = []
    for quality in (False, True):
        b, ft, _ = _bm(tmp_path / str(quality), quality=quality)
        b._Benchmarker__benchmark(ft, open(tmp_path / ("log%s" % quality), "w"))
        # everything but the generator object (its directory differs per run)
        reported.append(b.results.report_benchmark_results.call_args[0][1:])
        if quality:
            name, q, _image = b.results.add_quality.call_args[0]
            assert name == "hugo" and q["status"] == "error"
    assert reported[0] == reported[1]


def test_no_pass_without_results_or_with_failure(tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(runner, "run_pass", lambda *a: called.append(a) or {"status": "ok"})
    for i, kw in enumerate(({"results": []}, {"failure": "nonconformant: index"})):
        b, ft, _ = _bm(tmp_path / str(i), **kw)
        b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
        b.results.add_quality.assert_not_called()
    assert called == []


def test_skipped_cell_exports_nothing(tmp_path):
    b, ft, exports = _bm(tmp_path)
    b.config.suite_info = {"name": "P"}
    b.config.content_size = "50"
    b._Benchmarker__benchmark(ft, open(tmp_path / "log", "w"))
    assert exports == [None]
    b.results.add_quality.assert_not_called()


def test_results_add_quality(fake_benchmarker):
    res = Results(fake_benchmarker)
    res._environment = {"fingerprint": "f"}  # what environment.capture would have cached
    before = res._Results__to_jsonable()
    assert "quality" not in before and "quality" not in before["environment"]
    res.add_quality("hugo", {"status": "ok", "tools": {"lighthouse": "1.0.0"}}, "sha256:q")
    after = res._Results__to_jsonable()
    assert after["quality"] == {"hugo": {"status": "ok", "tools": {"lighthouse": "1.0.0"}}}
    assert after["rawData"] == before["rawData"] and after["succeeded"] == before["succeeded"]
    assert after["environment"] == {"fingerprint": "f",
                                    "quality": {"lighthouse": "1.0.0", "image": "sha256:q"}}


def test_reparse_keeps_quality(fake_benchmarker, monkeypatch):
    assert "quality" in STORED_RUN_KEYS
    monkeypatch.setattr(Results, "_Results__count_commits", lambda self: None)
    monkeypatch.setattr(Results, "_Results__count_sloc", lambda self: None)
    res = Results(fake_benchmarker)
    with open(res.file, "w") as f:
        json.dump({"quality": {"hugo": {"status": "ok"}}, "rawData": {"datarate": {}}}, f)
    res.reparse([])
    with open(res.file) as f:
        assert json.load(f)["quality"] == {"hugo": {"status": "ok"}}
```

- [ ] **Step 2: Run them and see them fail**

Run: `python3 -m pytest -q tests/test_quality_runner.py`
Expected: FAIL with `ImportError: cannot import name 'runner'`.

- [ ] **Step 3: Implement `toolset/quality/runner.py`**

```python
'''
The untimed quality pass of one generator (spec 009 R-1..R-3, R-16).
'''
import json
import os

from toolset.quality import reduce, site

# R-1: with --suite, the pass runs only in this (numberOfFiles, contentSize) cell
QUALITY_CELL = (50, 5.0)


def _cell(config):
    return int(config.number_of_files), float(config.content_size)


def eligible(config):
    if not getattr(config, 'quality', False):
        return False
    if getattr(config, 'suite_info', None) is None:
        return True
    return _cell(config) == QUALITY_CELL


def skipped(config):
    return bool(getattr(config, 'quality', False)) and not eligible(config)


def archive_path(results_dir, name):
    return os.path.join(results_dir, 'quality', name, 'site.tar')


def run_pass(docker_helper, test, results_dir):
    '''Runs the pass, writes quality.json and returns it. Never raises.'''
    out_dir = os.path.join(results_dir, 'quality', test.name)
    tar_path = archive_path(results_dir, test.name)
    try:
        output_folder, output_glob = site.generator_config(test.directory)
        if not os.path.exists(tar_path):
            raise RuntimeError('no exported output (%s)' % output_folder)
        site_dir = site.extract(tar_path, os.path.join(out_dir, 'site'))
        pages = site.resolve_pages(site_dir)
        site_name = os.path.basename(output_folder.rstrip('/'))
        raw = docker_helper.run_quality(tar_path, site_name, pages)
        with open(os.path.join(out_dir, 'raw.json'), 'w') as f:
            json.dump(raw, f, indent=2)
        quality = reduce.build_quality(raw, site_dir, pages, output_glob)
    except Exception as e:
        quality = {'status': 'error', 'error': '%s: %s' % (type(e).__name__, e)}
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'quality.json'), 'w') as f:
        json.dump(quality, f, indent=2)
    if os.path.exists(tar_path):
        os.remove(tar_path)
    return quality
```

- [ ] **Step 4: Add the flag**

In `toolset/run-tests.py`, after the `--no-cache` argument:

```python
    parser.add_argument(
        '--quality',
        action='store_true',
        default=False,
        help='After the timed runs, audit the output of the last build (Lighthouse, SEO '
             'signals, HTML, accessibility, links, weight); untimed. With --suite, only in '
             'the cell nf50-cs5 (spec 009)')
```

In `toolset/utils/benchmark_config.py`, after `self.no_cache = ...`:

```python
        self.quality = bool(getattr(args, 'quality', False))
```

- [ ] **Step 5: Hook the pass into `Benchmarker`**

In `toolset/benchmark/benchmarker.py`, add the imports `from toolset.quality import runner as quality_runner` and `from toolset.quality import site as quality_site` with the other `toolset` imports.

In `__benchmark.benchmark_type`, before `if not test.failed:`, add:

```python
            export = self.__quality_export(framework_test)
            self._quality_kwargs = {'export': export} if export else {}
```

Change both `self.docker_helper.benchmark(...)` calls, in `benchmark_type` and in `__noise_control`, to pass `**self._quality_kwargs` after `self.config.run_test_timeout_seconds`. In `__noise_control`, use `**getattr(self, '_quality_kwargs', {})`, because older tests call it directly.

After `self.results.report_benchmark_results(...)` in `benchmark_type`, add:

```python
            if export and results['results'] and not results.get('failureReason') \
                    and not results.get('unsupported'):
                self.__quality_pass(framework_test, benchmark_log)
```

Add the two methods to the class:

```python
    def __quality_export(self, framework_test):
        '''(output_folder, dest_tar) when the quality pass runs in this cell (spec 009 R-1).'''
        if quality_runner.skipped(self.config):
            log("quality: skipped (only cell nf50-cs5 of a suite)")
            return None
        if not quality_runner.eligible(self.config):
            return None
        try:
            output_folder, _glob = quality_site.generator_config(framework_test.directory)
        except Exception as e:
            log("quality: cannot read output_folder: %s" % e)
            return None
        return (output_folder,
                quality_runner.archive_path(self.results.directory, framework_test.name))

    def __quality_pass(self, framework_test, benchmark_log):
        '''Untimed; never changes the build result (spec 009 R-2).'''
        log("QUALITY PASS %s (untimed)" % framework_test.name, file=benchmark_log, border='*')
        quality = quality_runner.run_pass(self.docker_helper, framework_test, self.results.directory)
        self.results.add_quality(framework_test.name, quality,
                                 getattr(self.docker_helper, '_quality_image', None))
        log("quality: %s" % quality.get('status'), file=benchmark_log)
```

- [ ] **Step 6: Record quality in `Results`**

In `toolset/utils/results.py`:
- Add `'quality'` to the end of `STORED_RUN_KEYS`.
- In `__init__`, next to the other run attributes, set `self.quality = {}` and `self.quality_environment = None`.
- Add:

```python
    def add_quality(self, name, quality, image_id=None):
        '''results.json quality.<name> and environment.quality (spec 009 R-6, R-17).'''
        self.quality[name] = quality
        tools = quality.get('tools')
        if self.quality_environment is None and isinstance(tools, dict) \
                and not tools.get('error'):
            self.quality_environment = dict(tools, image=image_id)
```

- In `__to_jsonable`, replace `toRet['environment'] = self.__environment()` with:

```python
        env = self.__environment()
        if env is not None and self.quality_environment:
            env = dict(env, quality=self.quality_environment)
        toRet['environment'] = env
```

  Before the `toRet.update(getattr(self, '_stored_run', None) or {})` line, add:

```python
        if getattr(self, 'quality', None):
            toRet['quality'] = self.quality
```

- [ ] **Step 7: Run all tests**

Run: `python3 -m pytest -q && ruff check toolset tests`
Expected: all pass. That includes `tests/test_noise.py` and `tests/test_schema.py`, whose `bench` side effects take 6 positional arguments; without `--quality`, no `export` keyword is passed. If `test_schema.py` lists the allowed top-level keys of `results.json`, add `"quality": dict` to that mapping, because the key is only present after a quality pass.

- [ ] **Step 8: Commit**

```bash
git add toolset/quality/runner.py toolset/run-tests.py toolset/utils/benchmark_config.py \
        toolset/benchmark/benchmarker.py toolset/utils/results.py tests/test_quality_runner.py tests/test_schema.py
git commit -m "feat(quality): --quality runs the untimed pass after a successful build (spec 009 R-1, R-2, R-6, R-17)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: "Qualidade" in `summary.md` and `quality-summary.csv`

**Files:**
- Modify:
  - `toolset/utils/summary.py`: new functions after `to_markdown`, and one hook at the end of `to_markdown`;
  - `toolset/utils/results.py`: `write_summary`.
- Test: `tests/test_quality_summary.py`

**Interfaces:**
- Consumes: the `quality.json` contract (Task 3); `results.json` `quality` (Task 6).
- Produces: `QUALITY_COLUMNS`, `quality_rows(results)`, `quality_csv(rows)`, `quality_markdown(rows)`.

- [ ] **Step 1: Write the failing tests**

`tests/test_quality_summary.py`:

```python
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
```

- [ ] **Step 2: Run them and see them fail**

Run: `python3 -m pytest -q tests/test_quality_summary.py`
Expected: FAIL with `AttributeError: module 'toolset.utils.summary' has no attribute 'quality_rows'`.

- [ ] **Step 3: Implement in `toolset/utils/summary.py`**

Add after `to_markdown`:

```python
QUALITY_COLUMNS = ['framework', 'status', 'performance', 'accessibility', 'bestPractices', 'seo',
                   'lcpMs', 'postJsBytes', 'jsClass', 'gzipBytes', 'htmlErrors',
                   'a11yViolations', 'brokenLinks', 'seoPresent', 'seoTotal']
QUALITY_NOTE = ('The SF 005 templates carry no meta description and no viewport, so every '
                'generator loses the same Lighthouse SEO points; that is not a difference '
                'between generators.')


def _get(data, *path):
    for key in path:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _sum_pages(q, section, key):
    pages = _get(q, section, 'pages') or {}
    values = [p.get(key) for p in pages.values() if isinstance(p, dict) and p.get(key) is not None]
    return sum(values) if values else None


def _flatten(data, prefix=''):
    for key, value in (data or {}).items():
        name = prefix + str(key)
        if isinstance(value, dict):
            yield from _flatten(value, name + '.')
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            yield name, value


def quality_rows(results):
    '''One row per generator with a quality pass (spec 009 R-18), sorted by name.'''
    rows = []
    for name in sorted(results.get('quality') or {}):
        q = results['quality'][name]
        post = _get(q, 'lighthouse', 'mobile', 'post') or {}
        rows.append({
            'framework': name,
            'status': q.get('status'),
            'error': q.get('error'),
            'performance': _get(post, 'scores', 'performance', 'median'),
            'accessibility': _get(post, 'scores', 'accessibility', 'median'),
            'bestPractices': _get(post, 'scores', 'best-practices', 'median'),
            'seo': _get(post, 'scores', 'seo', 'median'),
            'lcpMs': _get(post, 'metrics', 'lcp', 'median'),
            'postJsBytes': _get(q, 'js', 'pages', 'post'),
            'jsClass': _get(q, 'js', 'jsClass'),
            'gzipBytes': _get(q, 'weight', 'gzipBytes'),
            'htmlErrors': _sum_pages(q, 'html', 'errors'),
            'a11yViolations': _sum_pages(q, 'a11y', 'total'),
            'brokenLinks': _get(q, 'links', 'broken'),
            'seoPresent': _get(q, 'seo', 'present', 'post'),
            'seoTotal': _get(q, 'seo', 'total'),
            'numeric': dict(_flatten({k: v for k, v in q.items() if k != 'tools'})),
        })
    return rows


def quality_csv(rows):
    extra = sorted({k for r in rows for k in r['numeric']})
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(QUALITY_COLUMNS + extra)
    for r in rows:
        writer.writerow([_blank(r[c]) for c in QUALITY_COLUMNS]
                        + [_blank(r['numeric'].get(k)) for k in extra])
    return out.getvalue()


def _score(value):
    return '—' if value is None else '%d' % round(value * 100)


def _kb(value):
    return '—' if value is None else '%.1f' % (value / 1024)


def _int(value):
    return '—' if value is None else '%d' % round(value)


def quality_markdown(rows):
    lines = ['## Qualidade', '',
             'Untimed pass over the output of the last build (spec 009). Scores and LCP: '
             'Lighthouse mobile preset on the post page, median of 3 runs. No combined score '
             'and no ranking.', '',
             '| Framework | Performance | Accessibility | Best practices | SEO | LCP (ms) '
             '| Post JS (KB) | JS | Gzip (KB) | HTML errors | axe violations | Broken links '
             '| SEO signals |',
             '|' + '---|' * 13]
    for r in rows:
        signals = '—' if r['seoPresent'] is None else '%s/%s' % (r['seoPresent'], r['seoTotal'])
        cells = [r['framework'], _score(r['performance']), _score(r['accessibility']),
                 _score(r['bestPractices']), _score(r['seo']), _int(r['lcpMs']),
                 _kb(r['postJsBytes']), r['jsClass'] or '—', _kb(r['gzipBytes']),
                 _int(r['htmlErrors']), _int(r['a11yViolations']), _int(r['brokenLinks']), signals]
        lines.append('| ' + ' | '.join(str(c) for c in cells) + ' |')
    lines += ['', '- ' + QUALITY_NOTE]
    for r in rows:
        if r['status'] == 'error':
            lines.append('- %s: %s' % (r['framework'], r['error']))
    return lines
```

Check that `summary.py` already imports `csv` and `io`, which `to_csv` needs; add them if not. Check that `_blank` maps `None` to `''`; if its behavior differs, use `'' if v is None else v` inline. At the end of `to_markdown`, replace `return '\n'.join(lines) + '\n'` with:

```python
    if meta.get('quality'):
        lines += [''] + quality_markdown(quality_rows(meta))
    return '\n'.join(lines) + '\n'
```

- [ ] **Step 4: Write `quality-summary.csv` in `Results.write_summary`**

In `toolset/utils/results.py` `write_summary`, after the `summary.md` write:

```python
            if data.get('quality'):
                with open(os.path.join(self.directory, 'quality-summary.csv'), 'w', newline='') as f:
                    f.write(summary.quality_csv(summary.quality_rows(data)))
```

- [ ] **Step 5: Run all tests**

Run: `python3 -m pytest -q && ruff check toolset tests`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add toolset/utils/summary.py toolset/utils/results.py tests/test_quality_summary.py
git commit -m "feat(quality): Qualidade section in summary.md and quality-summary.csv (spec 009 R-18, R-19)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: CI, the round workflow and docs

**Files:**
- Modify: `.github/workflows/ci.yml` (two new jobs), `.github/workflows/benchmark-round.yml` (a `quality` input), `README.md` (a "Quality pass" section after "Results")
- Test: CI itself, run on the PR.

**Interfaces:**
- Consumes: everything above.
- Produces: goal 4 of the spec.

- [ ] **Step 1: Add the CI jobs**

Append to `.github/workflows/ci.yml` under `jobs:`:

```yaml
  quality-image:
    needs: toolset
    strategy:
      matrix:
        runner: [ubuntu-24.04, ubuntu-24.04-arm]
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ssgberk/quality quality
      - name: Collector on the fixture site
        run: |
          docker run --rm --network none \
            -v "$PWD/tests/fixtures/quality/site:/fixture:ro" -v "$PWD/quality/test:/test:ro" \
            ssgberk/quality sh -c 'node /quality/run.mjs --site /fixture --pages "$(cat /test/pages.json)" --out /tmp/out \
              && node /test/check-shape.mjs /tmp/out/raw.json /test/expected-shape.json'

  quality:
    needs: quality-image
    strategy:
      matrix:
        runner: [ubuntu-24.04, ubuntu-24.04-arm]
    runs-on: ${{ matrix.runner }}
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
      - run: ./ssgberk --test hugo -nf 50 -cs 5 -mr 1 --quality
      - run: |
          R=$(ls -td results/*/ | head -1)
          jq -e '.rawData.datarate.hugo[0].mean > 0' "$R/results.json"
          jq -e '.quality.hugo.status == "ok"' "$R/results.json"
          for s in lighthouse seo html a11y links weight js extra; do
            jq -e --arg s "$s" '.quality.hugo[$s].status == "ok"' "$R/results.json"
          done
          jq -e '[.quality.hugo.lighthouse.mobile[], .quality.hugo.lighthouse.desktop[]
                  | .scores[] | .median | select(. < 0 or . > 1)] | length == 0' "$R/results.json"
          jq -e '.environment.quality.lighthouse and .environment.quality.chromium' "$R/results.json"
          test -s "$R/quality-summary.csv"
          grep -q '^## Qualidade' "$R/summary.md"
```

- [ ] **Step 2: Add the round input**

In `.github/workflows/benchmark-round.yml`, add to `workflow_dispatch.inputs`:

```yaml
      quality:
        description: Run the untimed quality pass (spec 009); with a suite, only in cell nf50-cs5
        type: boolean
        default: false
```

In the `run` job's "Run benchmark" step, add `QUALITY: ${{ inputs.quality }}` to `env`, and change the script to:

```bash
          Q=""
          if [ "$QUALITY" = "true" ]; then Q="--quality"; fi
          if [ -n "$SUITE" ]; then
            ./ssgberk --test "$TEST" --suite "$SUITE" --cell "$CELL" $Q
          else
            ./ssgberk --test "$TEST" -nf "$NF" -cs "$CS" -mr "$MR" $Q
          fi
```

This job already runs one job per generator. A failing check is a result, so the job still succeeds (spec goal 4).

- [ ] **Step 3: Document it**

Add to `README.md` after the "Results" section:

```markdown
## Quality pass

`--quality` audits the output of the last timed build of each generator, without timing it (spec `docs/specs/009-output-quality`):

        $ ./ssgberk --test hugo -nf 50 -cs 5 --quality

With `--suite`, the pass runs only in the cell `nf50-cs5` (suite P, cell 0). It builds the `ssgberk/quality` image from `quality/` once. That image pins Lighthouse, Playwright's Chromium, axe-core, html-validate and lychee. The image runs with no network and with the site copied in, and it audits the index, the first post and `404.html`:
- Lighthouse, mobile and desktop presets, median of 3 runs;
- SEO signals (title, lang, description, viewport, canonical, Open Graph, Twitter card, JSON-LD, robots, hreflang, headings, `alt`, plus `robots.txt`, `sitemap.xml`, feed and favicon);
- HTML validity, axe-core violations and broken internal links;
- weight on disk, gzip and brotli;
- JS bytes, and whether the post works without JS;
- files outside the reference page set.

Results go to `results/<ts>/quality/<generator>/quality.json`, to `quality` in `results.json`, to the "Qualidade" section of `summary.md` and to `quality-summary.csv`. They have no combined score and no ranking. A failing check is a result and never fails the run.
```

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest -q && ruff check toolset tests`, then validate the workflow files with `python3 -c "import yaml,sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" .github/workflows/ci.yml .github/workflows/benchmark-round.yml`. If PyYAML is not installed, use `ruby -ryaml -e 'ARGV.each { |f| YAML.load_file(f) }' .github/workflows/*.yml`.
Expected: all pass, and both files parse.

- [ ] **Step 5: Commit and push**

```bash
git add .github/workflows/ci.yml .github/workflows/benchmark-round.yml README.md
git commit -m "ci(quality): quality image and hugo quality pass on amd64 and arm64; round input (spec 009 goal 4)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
git push
```

Expected: the `quality-image` and `quality` CI jobs pass on both runners. If a Lighthouse audit id or lychee key differs on CI, fix it as described in Task 4 Step 6.
