#!/usr/bin/env python3
'''
Prints the generator directories (Lang/name) a CI run must smoke-test,
given the files changed against a base ref in an ssg-frameworks checkout.
Changes to the canonical build.sh or to CI config run every generator.
'''
import argparse
import glob
import os
import subprocess
import sys


def changed_tests(changed_files, all_test_dirs, canonical_build_sh="Go/hugo/build.sh"):
    if any(f == canonical_build_sh or f.startswith(".github/") for f in changed_files):
        return list(all_test_dirs)
    touched = {"/".join(f.split("/")[:2]) for f in changed_files if f.count("/") >= 2}
    return [d for d in all_test_dirs if d in touched]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--repo", required=True)
    args = parser.parse_args(argv)
    files = subprocess.check_output(
        ["git", "diff", "--name-only", "%s...HEAD" % args.base],
        cwd=args.repo, text=True).splitlines()
    all_dirs = sorted(
        os.path.dirname(os.path.relpath(p, args.repo))
        for p in glob.glob(os.path.join(args.repo, "*", "*", "benchmark_config.json")))
    for d in changed_tests(files, all_dirs):
        print(d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
