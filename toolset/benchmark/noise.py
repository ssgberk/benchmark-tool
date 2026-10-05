"""Noise control (spec 008 R-21): CV-based single re-run and the noisy flag."""

CV_THRESHOLD = 0.10
MAX_RERUN_RUNS = 10


def _cv(result):
    cv = result.get('cv') if result else None
    return cv if isinstance(cv, (int, float)) else None


def needs_rerun(result, runs, threshold=CV_THRESHOLD):
    cv = _cv(result)
    return int(runs) >= 3 and cv is not None and cv > threshold


def rerun_runs(runs):
    return min(2 * int(runs), MAX_RERUN_RUNS)


def finalize(attempts, threshold=CV_THRESHOLD):
    """The last attempt is the result; all attempts are summarized."""
    last = dict(attempts[-1])
    cv = _cv(last)
    last['attempts'] = [{'cv': a.get('cv'), 'median': a.get('median'),
                         'mean': a.get('mean'), 'stddev': a.get('stddev'),
                         'runs': len(a.get('times') or []) or None}
                        for a in attempts]
    last['noisy'] = cv is not None and cv > threshold
    return last
