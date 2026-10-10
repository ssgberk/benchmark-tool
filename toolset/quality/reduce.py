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
         'postSource': pages['post'].get('source'),
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
