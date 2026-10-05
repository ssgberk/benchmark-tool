'''
Merges per-generator results.json files (one GitHub Actions runner each)
into a single results.json plus summary.csv and summary.md.

Usage: python3 -m toolset.utils.merge_results --out DIR result1.json ...
'''
import argparse
import glob
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
    raw, ok, bad, names = {}, [], [], []
    for r in results:
        raw.update((r.get('rawData') or {}).get('datarate') or {})
        ok += (r.get('succeeded') or {}).get('datarate') or []
        bad += (r.get('failed') or {}).get('datarate') or []
        names += r.get('frameworks') or []
    starts = [r['startTime'] for r in results if r.get('startTime')]
    ends = [r['completionTime'] for r in results if r.get('completionTime')]
    merged.update({
        'name': DESCRIPTION,
        'environmentDescription': DESCRIPTION,
        'frameworks': sorted(set(names) | set(raw)),
        'rawData': {'datarate': raw},
        'succeeded': {'datarate': sorted(set(ok))},
        'failed': {'datarate': sorted(set(bad))},
        'startTime': min(starts) if starts else None,
        'completionTime': max(ends) if ends else None,
    })
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
    parser.add_argument('results', nargs='+', help='per-generator results.json')
    args = parser.parse_args(argv)

    results, languages, environments = [], {}, {}
    for path in args.results:
        data = _read_json(path)
        if not isinstance(data, dict):
            print('skipping unreadable %s' % path)
            continue
        results.append(data)
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

    merged = merge(results)
    if environments:
        merged['environments'] = dict(sorted(environments.items()))
    rows = summary.build_rows(merged, languages)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, 'results.json'), 'w') as f:
        json.dump(merged, f, indent=2)
    with open(os.path.join(args.out, 'summary.csv'), 'w', newline='') as f:
        f.write(summary.to_csv(rows))
    with open(os.path.join(args.out, 'summary.md'), 'w') as f:
        f.write(summary.to_markdown(rows, merged))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
