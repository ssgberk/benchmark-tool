'''
Ranking groups, overlap ranking and scaling exponent (spec 008, R-24 and R-25).
'''
import math

NOT_RANKED_LEGACY = 'not ranked: legacy results (no schemaVersion)'
NOT_RANKED_CONCURRENT = 'not ranked: concurrent run'
NOT_RANKED_NO_FINGERPRINT = 'not ranked: no environment fingerprint'
NOT_RANKED_SUITE = 'not ranked: suite is not ranked'


def fingerprint_of(results):
    env = results.get('environment')
    if not isinstance(env, dict):
        return ''
    return env.get('fingerprint') or ''


def fingerprint_for(results, name):
    '''Per-framework fingerprint (merged rounds) else the top-level one.'''
    fps = results.get('fingerprints')
    if isinstance(fps, dict):
        return fps.get(name) or ''
    return fingerprint_of(results)


def not_ranked_reason(results):
    '''Returns why a results dict cannot be ranked, or None when it can.'''
    if not results.get('schemaVersion'):
        return NOT_RANKED_LEGACY
    suite = results.get('suite')
    if isinstance(suite, dict) and suite.get('ranked') is False:
        return NOT_RANKED_SUITE
    if (results.get('protocol') or {}).get('concurrent'):
        return NOT_RANKED_CONCURRENT
    fps = results.get('fingerprints')
    if isinstance(fps, dict):
        if not any(fps.values()):
            return NOT_RANKED_NO_FINGERPRINT
    elif not fingerprint_of(results):
        return NOT_RANKED_NO_FINGERPRINT
    return None


def group_key(result_meta, row):
    '''
    (suite, suiteVersion, numberOfFiles, contentSize, profile, fingerprint, features)
    Row values win over the top-level metadata, so rows merged from several
    results.json files keep their own group.
    '''
    suite = result_meta.get('suite')
    suite = suite if isinstance(suite, dict) else {}

    def pick(name, fallback):
        value = row.get(name)
        return fallback if value in (None, '') else value

    return (str(pick('suite', suite.get('name') or '')),
            str(pick('suiteVersion', suite.get('version') or '')),
            str(row.get('numberOfFiles', '')),
            str(row.get('contentSize', '')),
            str(pick('profile', result_meta.get('profile') or '')),
            str(row['fingerprint'] if 'fingerprints' in result_meta
                else pick('fingerprint', fingerprint_of(result_meta))),
            str(row.get('features') or ''))


def _num(value):
    if value in ('', None):
        return None
    return float(value)


def rank(rows):
    '''
    Rank labels for rows of ONE group, aligned with the input order.
    Sort by median; a row shares the previous row's rank when its min is
    <= the previous row's max (shown "=n"). Rows without a median get ''.
    '''
    labels = [''] * len(rows)
    order = sorted((i for i, r in enumerate(rows) if _num(r.get('median')) is not None),
                   key=lambda i: (_num(rows[i]['median']), i))
    ranks, shared = [], []
    for pos, i in enumerate(order, 1):
        if pos > 1:
            prev = rows[order[pos - 2]]
            lo, hi = _num(rows[i].get('min')), _num(prev.get('max'))
            if lo is None:
                lo = _num(rows[i]['median'])
            if hi is None:
                hi = _num(prev['median'])
            if lo <= hi:
                ranks.append(ranks[-1])
                shared[-1] = True
                shared.append(True)
                continue
        ranks.append(pos)
        shared.append(False)
    for i, r, s in zip(order, ranks, shared):
        labels[i] = ('=%d' if s else '%d') % r
    return labels


def scaling_exponent(points):
    '''
    Least-squares slope of log10(median) on log10(nf); None below 3 usable points.
    '''
    xy = [(math.log10(n), math.log10(m)) for n, m in points
          if n and m and float(n) > 0 and float(m) > 0]
    if len(xy) < 3:
        return None
    mx = sum(x for x, _ in xy) / len(xy)
    my = sum(y for _, y in xy) / len(xy)
    sxx = sum((x - mx) ** 2 for x, _ in xy)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in xy) / sxx
