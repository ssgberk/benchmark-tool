import csv
import io
import json
import os
from datetime import datetime, timezone

from toolset.utils import ranking

BASE_COLUMNS = ['framework', 'language', 'numberOfFiles', 'contentSize', 'minRuns',
                'mean', 'stddev', 'median', 'min', 'max', 'status']
METHOD_COLUMNS = ['suite', 'suiteVersion', 'profile', 'features', 'fingerprint',
                  'cv', 'noisy', 'attempts', 'user', 'system', 'cpuUtilization',
                  'peakRssMB', 'inputMB', 'outputFiles', 'outputMB',
                  'postsPerSecond', 'inputMBPerSecond', 'imageBuildSeconds',
                  'failureReason']
COLUMNS = BASE_COLUMNS + METHOD_COLUMNS
STATS = ['mean', 'stddev', 'median', 'min', 'max']
NUMERIC = ['cv', 'user', 'system', 'cpuUtilization', 'peakRssMB', 'inputMB',
           'outputFiles', 'outputMB', 'postsPerSecond', 'inputMBPerSecond']
NOISY_SUFFIX = ' \u26a0'
FAIL_STATUSES = ('timeout', 'oom', 'nonconformant', 'unsupported')

CAVEATS = {
    'T1': 'T1: Docker Desktop runs the generators in a Linux VM whose vCPUs are '
          'time-shared with the host and whose disk is virtualised. Absolute times '
          'are not comparable with native Linux and are noisier.',
    'T5': 'T5: at 100 files or fewer, bundler-dominated JavaScript generators '
          '(Gatsby, Next.js, Astro, VitePress) mostly measure bundler start-up, '
          'not content handling. Read the full matrix and the scaling exponent; '
          'never quote one small cell as the result.',
    'T7': 'T7: peak RSS is the largest single process, not the sum, so it '
          'under-reports multi-process generators.',
    'T9': 'T9: oom means the generator exceeded the container memory limit, which is '
          'the same for every generator; it is an outcome, not a time.',
    'concurrent': 'Concurrent: other ssgberk benchmark containers were running when '
                  'this run started, so its results may be affected and are not ranked.',
    'legacy-2019': 'Legacy: the legacy-2019 suite is for historical comparison '
                   'only and is never ranked against the others.',
}


def _blank(value):
    return '' if value is None else value


def _num(value, scale=1.0, digits=None):
    if value is None:
        return ''
    out = value / scale if scale != 1.0 else value
    return round(out, digits) if digits is not None else out


def _fill_method(row, data, results, name):
    suite = results.get('suite') if isinstance(results.get('suite'), dict) else {}
    row['suite'] = _blank(suite.get('name'))
    row['suiteVersion'] = _blank(suite.get('version'))
    row['profile'] = _blank(results.get('profile'))
    row['fingerprint'] = ranking.fingerprint_for(results, name)
    build = (results.get('imageBuild') or {}).get(name) or {}
    row['imageBuildSeconds'] = _num(build.get('seconds'), digits=3)
    if data is None:
        return
    row['features'] = ','.join(sorted(data.get('features') or []))
    row['cv'] = _num(data.get('cv'))
    if data.get('noisy') is not None:
        row['noisy'] = 'true' if data['noisy'] else 'false'
    if data.get('attempts'):
        row['attempts'] = len(data['attempts'])
    for key in ('user', 'system', 'cpuUtilization', 'outputFiles',
                'postsPerSecond', 'inputMBPerSecond'):
        row[key] = _blank(data.get(key))
    row['peakRssMB'] = _num(data.get('peakRssBytes'), 1e6, 2)
    row['inputMB'] = _num(data.get('inputBytes'), 1e6, 2)
    row['outputMB'] = _num(data.get('outputBytes'), 1e6, 2)


def _failure_status(name, results, reasons):
    if name in ((results.get('unsupported') or {}).get('datarate') or []):
        return 'unsupported'
    reason = str(reasons.get(name) or '')
    for status in ('timeout', 'oom', 'nonconformant'):
        if reason == status or reason.startswith(status + ':') or \
                reason.startswith(status + ' '):
            return status
    return 'failed'


def build_rows(results, tests_metadata):
    '''
    Builds one row per framework from a results.json dict.
    tests_metadata maps framework name -> language.
    Order: ok rows by mean ascending, then failed, then excluded.
    Each row also carries a non-CSV `rank` label (empty when not ranked).
    '''
    raw = results.get('rawData', {}).get('datarate', {})
    excluded = set(results.get('excluded') or [])
    reasons = results.get('failureReasons') or {}
    names = list(results.get('frameworks') or [])
    for name in list(raw) + list(excluded):
        if name not in names:
            names.append(name)

    ok, failed, skipped = [], [], []
    for name in names:
        row = dict.fromkeys(COLUMNS, '')
        row['framework'] = name
        row['language'] = tests_metadata.get(name) or ''
        data = raw[name][0] if raw.get(name) else None
        _fill_method(row, data, results, name)
        if name in excluded:
            row['status'] = 'excluded'
            skipped.append(row)
        elif data is not None and data.get('status', 'ok') == 'ok':
            for key in ['numberOfFiles', 'contentSize', 'minRuns'] + STATS:
                row[key] = _blank(data.get(key))
            row['status'] = 'ok'
            ok.append(row)
        else:
            if data is not None:  # a stored non-ok result: keep its status, no numbers
                status = data.get('status')
                row['status'] = status if status in FAIL_STATUSES else 'failed'
                for key in NUMERIC + ['noisy', 'attempts']:
                    row[key] = ''
            else:
                row['status'] = _failure_status(name, results, reasons)
            row['failureReason'] = _blank(reasons.get(name))
            for key in ('numberOfFiles', 'contentSize'):
                if row[key] == '':
                    row[key] = _blank(results.get(key))
            failed.append(row)

    ok.sort(key=lambda r: (r['mean'] == '', r['mean'] or 0, r['framework']))
    failed.sort(key=lambda r: r['framework'])
    skipped.sort(key=lambda r: r['framework'])
    rows = ok + failed + skipped
    _assign_ranks(rows, results)
    return rows


def _groups(rows, results):
    groups = {}
    for r in rows:
        if r['status'] == 'ok':
            groups.setdefault(ranking.group_key(results, r), []).append(r)
    return groups


def _assign_ranks(rows, results):
    for r in rows:
        r['rank'] = ''
    if ranking.not_ranked_reason(results):
        return
    rankable = [r for r in rows if r['fingerprint']]
    for members in _groups(rankable, results).values():
        for r, label in zip(members, ranking.rank(members)):
            r['rank'] = label


def to_csv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator='\n',
                            extrasaction='ignore')
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


def _fmt(value, digits=2):
    if value in ('', None):
        return '\u2014'
    return ('%.' + str(digits) + 'f') % float(value)


def _cv(value):
    return '\u2014' if value in ('', None) else '%.1f%%' % (float(value) * 100)


def _name(row):
    return row['framework'] + (NOISY_SUFFIX if row.get('noisy') == 'true' else '')


def _is_int(value):
    try:
        int(value)
        return True
    except (TypeError, ValueError):
        return False


def _header_line(meta, rows):
    parts = []
    suite = meta.get('suite') if isinstance(meta.get('suite'), dict) else None
    if suite:
        text = 'Suite: %s v%s' % (suite.get('name'), suite.get('version'))
        if suite.get('cellIndex') is not None and suite.get('cellCount'):
            text += ' \u00b7 cell %d/%d' % (suite['cellIndex'] + 1, suite['cellCount'])
        parts.append(text)
    nf, cs = meta.get('numberOfFiles'), meta.get('contentSize')
    if suite and nf is not None and cs is not None:
        parts.append('(nf %s, cs %s)' % (nf, cs))
    if meta.get('profile') and (suite or meta.get('schemaVersion')):
        parts.append('profile %s' % meta['profile'])
    if isinstance(meta.get('fingerprints'), dict):
        fps = {v for v in meta['fingerprints'].values() if v}
        fp = fps.pop() if len(fps) == 1 and all(meta['fingerprints'].values()) else ''
    else:
        fp = ranking.fingerprint_of(meta)
    if fp:
        parts.append('fingerprint %s' % fp)
    res = meta.get('resources')
    if isinstance(res, dict) and res.get('cpus') is not None:
        text = 'resources %g CPU' % res['cpus']
        if res.get('memoryBytes'):
            text += ' / %.1f GB' % (res['memoryBytes'] / 2 ** 30)
        if res.get('cpuset'):
            text += ' / cpuset %s' % res['cpuset']
        parts.append(text)
    if not parts:
        return None
    # "(nf, cs)" belongs to the cell part, the rest is separated by middle dots
    line = parts[0]
    for part in parts[1:]:
        line += (' ' if part.startswith('(') else ' \u00b7 ') + part
    return line


def _ranking_section(rows, reason):
    lines = ['', '## Ranking', '']
    groups = {}
    for r in rows:
        if r.get('rank'):
            groups.setdefault(ranking.group_key({}, r), []).append(r)
    if reason or not groups:
        lines.append(reason or 'not ranked: no successful results')
        return lines
    lines.append('Ordered by median; generators whose min\u2013max ranges overlap share a '
                 'rank (`=n`). Only results of the same suite, cell, profile, '
                 'fingerprint and feature set are ranked together.')
    for key, members in groups.items():
        suite, version, nf, cs, profile, fp, features = key
        lines += ['', '### %s' % ' \u00b7 '.join(
            [p for p in (('%s v%s' % (suite, version)) if suite else '',
                         'nf %s, cs %s' % (nf, cs), 'profile %s' % profile if profile else '',
                         'fingerprint %s' % fp if fp else '',
                         'features %s' % features if features else '') if p]), '',
                  '| Rank | Framework | Median (s) | CV | Min\u2013Max (s) |',
                  '|---|---|---|---|---|']
        order = sorted(members, key=lambda r: (float(r['median']), r['framework']))
        for r in order:
            lines.append('| %s | %s | %s | %s | %s\u2013%s |' % (
                r['rank'], _name(r), _fmt(r['median'], 3), _cv(r['cv']),
                _fmt(r['min'], 3), _fmt(r['max'], 3)))
    return lines


def _caveats(rows, meta):
    keys = []
    texts = dict(CAVEATS)
    docker = (meta.get('environment') or {}).get('docker') or {}
    if 'Docker Desktop' in str(docker.get('operatingSystem') or ''):
        keys.append('T1')
    if any(r.get('noisy') == 'true' for r in rows):
        keys.append('noisy')
        threshold = (meta.get('protocol') or {}).get('cvThreshold')
        texts['noisy'] = ('Noisy: results marked \u26a0 had a CV above %g%% '
                          '(protocol cvThreshold) on their last attempt.'
                          % (100 * (0.10 if threshold is None else threshold)))
    if (meta.get('protocol') or {}).get('concurrent'):
        keys.append('concurrent')
    if (meta.get('suite') or {}).get('name') == 'legacy-2019':
        keys.append('legacy-2019')
    ok = [r for r in rows if r['status'] == 'ok']
    if meta.get('schemaVersion') and any(
            _is_int(r['numberOfFiles']) and int(r['numberOfFiles']) <= 100 for r in ok):
        keys.append('T5')
    if any(r['status'] == 'oom' for r in rows):
        keys.append('T9')
    if keys and any(r.get('peakRssMB') not in ('', None) for r in ok):
        keys.append('T7')
    if not keys:
        return []
    return ['', '## Caveats', ''] + ['- ' + texts[k] for k in keys]


def _failed_section(rows):
    lines = ['', '## Failed / timeout / oom / nonconformant / unsupported', '']
    bad = [r for r in rows if r['status'] != 'ok']
    if bad:
        for r in bad:
            line = '- %s (%s)' % (r['framework'], r['status'])
            if r.get('failureReason'):
                line += ': %s' % r['failureReason']
            lines.append(line)
    else:
        lines.append('None.')
    return lines


def to_markdown(rows, meta):
    lines = ['# %s' % (meta.get('name') or 'SSGBerk results'), '']
    lines.append('- Environment: %s' % (meta.get('environmentDescription') or '\u2014'))
    lines.append('- Started: %s' % _when(meta.get('startTime')))
    lines.append('- Completed: %s' % _when(meta.get('completionTime')))
    commit = (meta.get('git') or {}).get('commitId')
    if commit:
        lines.append('- Commit: %s' % commit)
    header = _header_line(meta, rows)
    if header:
        lines += ['', header]
    lines += ['', '| Framework | Language | Files | Size (KB) | Min runs | Mean (s) '
              '| Stddev (s) | Median (s) | Min (s) | Max (s) | Status | Rank | CV '
              '| Posts/s | MB/s | CPU (cores) | Peak RSS (MB) | Output (MB / files) '
              '| Image build (s) |',
              '|' + '---|' * 19]
    for r in rows:
        output = '\u2014' if r['outputMB'] == '' else '%s / %s' % (
            _fmt(r['outputMB'], 1), r['outputFiles'])
        cells = [_name(r), r['language'] or '\u2014',
                 r['numberOfFiles'] or '\u2014', r['contentSize'] or '\u2014',
                 r['minRuns'] or '\u2014'] + [_seconds(r[k]) for k in STATS] + [
                 r['status'], r.get('rank') or '\u2014', _cv(r['cv']),
                 _fmt(r['postsPerSecond'], 1), _fmt(r['inputMBPerSecond'], 1),
                 _fmt(r['cpuUtilization']), _fmt(r['peakRssMB'], 1), output,
                 _fmt(r['imageBuildSeconds'], 1)]
        lines.append('| ' + ' | '.join(str(c) for c in cells) + ' |')
    lines += _ranking_section(rows, ranking.not_ranked_reason(meta))
    lines += _caveats(rows, meta)
    lines += _failed_section(rows)
    return '\n'.join(lines) + '\n'


def _read_json(path):
    with open(path) as f:
        return json.load(f)


SUITE_COLUMNS = ['cell'] + COLUMNS


def cell_name(number_of_files, content_size):
    return 'nf%s-cs%s' % (number_of_files, content_size)


def suite_csv(rows):
    '''suite-summary.csv text; rows carry a `cell` key. Shared by both writers.'''
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=SUITE_COLUMNS, lineterminator='\n',
                            extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def suite_summary(suite_dir, tests_metadata=None):
    '''
    Builds the suite-level files for results/<ts>/ from suite.json and the
    per-cell results.json. Returns (suite_summary_csv, suite_summary_md, scaling_csv).
    Cells whose results.json is missing are skipped; an aborted suite is noted.
    '''
    tests_metadata = tests_metadata or {}
    suite_doc = _read_json(os.path.join(suite_dir, 'suite.json'))
    all_rows, cells, reasons, meta = [], [], set(), {}
    for cell in suite_doc.get('cells') or []:
        path = os.path.join(suite_dir, cell.get('dir', ''), 'results.json')
        try:
            results = _read_json(path)
        except (OSError, ValueError):
            continue
        meta = meta or results
        rows = build_rows(results, tests_metadata)
        name = cell_name(cell.get('numberOfFiles'), cell.get('contentSize'))
        for r in rows:
            r['cell'] = name
            for key in ('numberOfFiles', 'contentSize'):
                if r[key] == '' and r['status'] != 'excluded':
                    r[key] = cell.get(key, '')
        reason = ranking.not_ranked_reason(results)
        if reason:
            reasons.add(reason)
        cells.append((cell, results, rows))
        all_rows += rows

    scaling = _scaling(all_rows)
    scaling_out = io.StringIO()
    sw = csv.writer(scaling_out, lineterminator='\n')
    sw.writerow(['framework', 'profile', 'contentSize', 'numberOfFiles', 'median'])
    for (fw, profile, cs), points in scaling.items():
        if len(points) >= 2:
            for nf, median in points:
                sw.writerow([fw, profile, cs, nf, median])

    lines = ['# Suite %s v%s' % (suite_doc.get('suite'), suite_doc.get('version')), '',
             '- Profile: %s' % (suite_doc.get('profile') or '\u2014'),
             '- Started: %s' % _when(suite_doc.get('startTime')),
             '- Completed: %s' % _when(suite_doc.get('completionTime')),
             '- Cells with results: %d of %d' % (len(cells), len(suite_doc.get('cells') or []))]
    if suite_doc.get('fingerprint'):
        lines.append('- Fingerprint: %s' % suite_doc['fingerprint'])
    if suite_doc.get('aborted'):
        lines.append('- ABORTED: %s' % suite_doc['aborted'])
    for reason in sorted(reasons):
        lines.append('- %s' % reason)
    lines += ['', '## Medians (s)', '']
    for cell, results, rows in cells:
        lines += ['', '### nf %s, cs %s' % (cell.get('numberOfFiles'), cell.get('contentSize')),
                  '', '| Rank | Framework | Median (s) | CV | Status |', '|---|---|---|---|---|']
        for r in sorted(rows, key=lambda r: (r['status'] != 'ok', r['median'] == '',
                                             r['median'] or 0, r['framework'])):
            if r['status'] != 'excluded':
                lines.append('| %s | %s | %s | %s | %s |' % (
                    r.get('rank') or '\u2014', _name(r), _seconds(r['median']),
                    _cv(r['cv']), r['status']))
    lines += ['', '## Scaling exponent', '',
              'Log-log slope b of `median ~ a * nf^b` per generator and content size; '
              'needs at least 3 cells. b near 1 is linear, below 1 fixed overhead '
              'dominates, above 1 is superlinear.', '',
              '| Framework | Profile | Content size | Cells | Scaling exponent |',
              '|---|---|---|---|---|']
    for (fw, profile, cs), points in scaling.items():
        if len(points) < 2:
            continue
        b = ranking.scaling_exponent(points)
        lines.append('| %s | %s | %s | %d | %s |' % (
            fw, profile or '\u2014', cs, len(points), '\u2014' if b is None else '%.2f' % b))
    lines += _caveats(all_rows, meta)
    return suite_csv(all_rows), '\n'.join(lines) + '\n', scaling_out.getvalue()


def _scaling(rows):
    groups = {}
    for r in rows:
        if r['status'] == 'ok' and _is_int(r['numberOfFiles']) and r['median'] != '':
            key = (r['framework'], r['profile'], str(r['contentSize']))
            groups.setdefault(key, []).append((int(r['numberOfFiles']), float(r['median'])))
    return {k: sorted(v) for k, v in sorted(groups.items())}


def write_suite_summary(suite_dir, tests_metadata=None):
    '''Writes suite-summary.csv, suite-summary.md and scaling.csv into suite_dir.'''
    csv_text, md, scaling_csv = suite_summary(suite_dir, tests_metadata)
    for name, text in (('suite-summary.csv', csv_text), ('suite-summary.md', md),
                       ('scaling.csv', scaling_csv)):
        with open(os.path.join(suite_dir, name), 'w', newline='') as f:
            f.write(text)
