'''
Builds the GitHub Actions job matrix (generator x suite cell) for the
benchmark-round workflow from toolset/benchmark/suites.json.

Usage: python3 -m toolset.github_actions.suite_matrix --suite P --tests hugo zola
'''
import argparse
import json
import sys

from toolset.benchmark import suites

MAX_JOBS = 256  # GitHub Actions matrix limit


def build_matrix(suite_name, tests, path=suites.DEFAULT):
    try:
        suite = suites.load(suite_name, path=path)
    except suites.SuiteError as e:
        raise ValueError(str(e))
    matrix = [{
        'test': test,
        'suite': suite.name,
        'cell': index,
        'number_of_files': str(cell.number_of_files),
        'content_size': cell.content_size,
        'min_runs': str(suite.runs),
        'key': '%s-%s-%d' % (test, suite.name, index),
    } for test in tests for index, cell in enumerate(suite.cells)]
    if len(matrix) > MAX_JOBS:
        raise ValueError('matrix has %d jobs, the limit is %d' % (len(matrix), MAX_JOBS))
    return matrix


def main(argv=None):
    parser = argparse.ArgumentParser(prog='suite_matrix')
    parser.add_argument('--suite', required=True)
    parser.add_argument('--tests', nargs='+', required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build_matrix(args.suite, args.tests), separators=(',', ':')))
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
