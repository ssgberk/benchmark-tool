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
