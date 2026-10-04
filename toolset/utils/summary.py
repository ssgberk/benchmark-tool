import csv
import io
from datetime import datetime, timezone

COLUMNS = ['framework', 'language', 'numberOfFiles', 'contentSize', 'minRuns',
           'mean', 'stddev', 'median', 'min', 'max', 'status']
STATS = ['mean', 'stddev', 'median', 'min', 'max']


def _blank(value):
    return '' if value is None else value


def build_rows(results, tests_metadata):
    '''
    Builds one row per framework from a results.json dict.
    tests_metadata maps framework name -> language.
    Order: ok rows by mean ascending, then failed, then excluded.
    '''
    raw = results.get('rawData', {}).get('datarate', {})
    excluded = set(results.get('excluded') or [])
    names = list(results.get('frameworks') or [])
    for name in list(raw) + list(excluded):
        if name not in names:
            names.append(name)

    ok, failed, skipped = [], [], []
    for name in names:
        row = dict.fromkeys(COLUMNS, '')
        row['framework'] = name
        row['language'] = tests_metadata.get(name) or ''
        if name in excluded:
            row['status'] = 'excluded'
            skipped.append(row)
        elif raw.get(name):
            data = raw[name][0]
            for key in ['numberOfFiles', 'contentSize', 'minRuns'] + STATS:
                row[key] = _blank(data.get(key))
            row['status'] = 'ok'
            ok.append(row)
        else:
            row['status'] = 'failed'
            failed.append(row)

    ok.sort(key=lambda r: (r['mean'] == '', r['mean'] or 0, r['framework']))
    failed.sort(key=lambda r: r['framework'])
    skipped.sort(key=lambda r: r['framework'])
    return ok + failed + skipped


def to_csv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def _seconds(value):
    if value in ('', None):
        return '—'
    return '%.3f' % float(value)


def _when(ms):
    if not ms:
        return '—'
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime(
        '%Y-%m-%d %H:%M:%S UTC')


def to_markdown(rows, meta):
    lines = ['# %s' % (meta.get('name') or 'SSGBerk results'), '']
    lines.append('- Environment: %s' % (meta.get('environmentDescription') or '—'))
    lines.append('- Started: %s' % _when(meta.get('startTime')))
    lines.append('- Completed: %s' % _when(meta.get('completionTime')))
    commit = (meta.get('git') or {}).get('commitId')
    if commit:
        lines.append('- Commit: %s' % commit)
    lines += ['', '| Framework | Language | Files | Size (KB) | Min runs | Mean (s) '
              '| Stddev (s) | Median (s) | Min (s) | Max (s) | Status |',
              '|---|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        cells = [r['framework'], r['language'] or '—',
                 r['numberOfFiles'] or '—', r['contentSize'] or '—',
                 r['minRuns'] or '—'] + [_seconds(r[k]) for k in STATS] + [r['status']]
        lines.append('| ' + ' | '.join(str(c) for c in cells) + ' |')
    lines += ['', '## Failed', '']
    bad = [r for r in rows if r['status'] != 'ok']
    if bad:
        lines += ['- %s (%s)' % (r['framework'], r['status']) for r in bad]
    else:
        lines.append('None.')
    return '\n'.join(lines) + '\n'
