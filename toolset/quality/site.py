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
    # join without a separator, as textContent does, so inline markup does not
    # insert spaces ("See <a>x</a>." -> "See x."); whitespace is collapsed after
    return re.sub(r'\s+', ' ', ''.join(parser.parts)).strip()


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
