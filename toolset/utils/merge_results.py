'''
Merges per-generator results.json files (one GitHub Actions runner each)
into a single results.json plus summary.csv and summary.md.

Usage: python3 -m toolset.utils.merge_results --out DIR result1.json ...
'''
import argparse
import csv
import glob
import io
import json
import os
import uuid

from toolset.utils import summary

DESCRIPTION = 'GitHub Actions ubuntu-24.04, one runner per generator'


def merge(results):
    '''Merges a list of results.json dicts into one results.json dict.'''
    merged = {}
    for r in results:
        for key, value in r.items():
            merged.setdefault(key, value)
    raw, ok, bad, names, completed = {}, [], [], [], {}
    for r in results:
        completed.update(r.get('completed') or {})
        raw.update((r.get('rawData') or {}).get('datarate') or {})
        ok += (r.get('succeeded') or {}).get('datarate') or []
        bad += (r.get('failed') or {}).get('datarate') or []
        names += r.get('frameworks') or []
    starts = [r['startTime'] for r in results if r.get('startTime')]
    ends = [r['completionTime'] for r in results if r.get('completionTime')]
    merged.update({
        'completed': completed,
        'git': next((r['git'] for r in results if r.get('git')), None),
        'name': DESCRIPTION,
        'environmentDescription': DESCRIPTION,
        'frameworks': sorted(set(names) | set(raw)),
        'rawData': {'datarate': raw},
        'succeeded': {'datarate': sorted(set(ok))},
        'failed': {'datarate': sorted(set(bad))},
        'startTime': min(starts) if starts else None,
        'completionTime': max(ends) if ends else None,
    })
    # Spec 008 sections: per-framework dicts are unioned across inputs, run-level
    # keys keep the first non-null value, schemaVersion is 2 if any input is 2.
    for key in ('failureReasons', 'imageBuild', 'generators'):
        if any(key in r for r in results):
            combined = {}
            for r in results:
                combined.update(r.get(key) or {})
            merged[key] = combined
    if any('unsupported' in r for r in results):
        merged['unsupported'] = {'datarate': sorted(
            {n for r in results for n in (r.get('unsupported') or {}).get('datarate') or []})}
    for key in ('resources', 'protocol', 'environment', 'suite', 'profile'):
        if key in merged and merged[key] is None:
            merged[key] = next((r[key] for r in results if r.get(key) is not None), None)
    merged.pop('schemaVersion', None)
    if any(r.get('schemaVersion') == 2 for r in results):
        merged['schemaVersion'] = 2
    merged['uuid'] = str(uuid.uuid4())
    return merged


def _read_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def main(argv=None):
    parser = argparse.ArgumentParser(prog='merge_results')
    parser.add_argument('--out', required=True, help='output directory')
    parser.add_argument('--by-cell', action='store_true',
                        help='group inputs by (numberOfFiles, contentSize); write one '
                             'results.json/summary per cell under DIR/nf<nf>-cs<cs>/ '
                             'plus suite-summary.csv/md')
    parser.add_argument('results', nargs='+', help='per-generator results.json')
    args = parser.parse_args(argv)

    results, languages, environments, cells = [], {}, {}, {}
    for path in args.results:
        data = _read_json(path)
        if not isinstance(data, dict):
            print('skipping unreadable %s' % path)
            continue
        results.append(data)
        cells.setdefault(cell_name(data), []).append(data)
        folder = os.path.dirname(os.path.abspath(path))
        for t in _read_json(os.path.join(folder, 'test_metadata.json'), []) or []:
            if isinstance(t, dict) and t.get('name'):
                languages[t['name']] = t.get('language') or ''
        for env in glob.glob(os.path.join(folder, 'env-*.txt')):
            name = os.path.basename(env)[len('env-'):-len('.txt')]
            with open(env, errors='replace') as f:
                environments[name] = f.read()
    if not results:
        print('no readable results')
        return 1

    if args.by_cell:
        suite_rows = []
        for cell, items in sorted(cells.items()):
            merged = merge(items)
            names = set(merged['frameworks'])
            write_outputs(merged, {k: v for k, v in languages.items() if k in names},
                          {k: v for k, v in environments.items() if k in names},
                          os.path.join(args.out, cell))
            for row in summary.build_rows(merged, languages):
                suite_rows.append(dict(row, cell=cell))
        write_suite_summary(suite_rows, args.out)
        return 0

    write_outputs(merge(results), languages, environments, args.out)
    return 0


def cell_name(data):
    return 'nf%s-cs%s' % (data.get('numberOfFiles'), data.get('contentSize'))


def write_outputs(merged, languages, environments, out):
    if environments:
        merged['environments'] = dict(sorted(environments.items()))
    rows = summary.build_rows(merged, languages)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'results.json'), 'w') as f:
        json.dump(merged, f, indent=2)
    with open(os.path.join(out, 'summary.csv'), 'w', newline='') as f:
        f.write(summary.to_csv(rows))
    with open(os.path.join(out, 'summary.md'), 'w') as f:
        f.write(summary.to_markdown(rows, merged))


def write_suite_summary(rows, out):
    '''One CSV and one Markdown table covering every cell of the suite.'''
    os.makedirs(out, exist_ok=True)
    columns = ['cell'] + summary.COLUMNS
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator='\n',
                            extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    with open(os.path.join(out, 'suite-summary.csv'), 'w', newline='') as f:
        f.write(buf.getvalue())
    lines = ['# Suite summary', '',
             '| Cell | Framework | Language | Mean (s) | Median (s) | Status |',
             '|---|---|---|---|---|---|']
    for r in rows:
        lines.append('| %s | %s | %s | %s | %s | %s |' % (
            r['cell'], r['framework'], r['language'] or '—',
            summary._seconds(r['mean']), summary._seconds(r['median']), r['status']))
    with open(os.path.join(out, 'suite-summary.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
