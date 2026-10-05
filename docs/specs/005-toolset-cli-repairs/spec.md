# 005 Toolset CLI repairs: spec

## What and why
Pre-existing defects found reviewing the Python 3 port. Each is fixed minimally and pinned by a test.

## Requirements
1. `--parse <ts>` re-parses raw.txt of an existing results dir via `Results.parse_all(test)` and rewrites results.json (previously called nonexistent `test.parse_all()`). Metadata of the original run (uuid, name, environmentDescription, git, startTime, completionTime, completed, frameworks) is preserved by loading the existing results.json; only rawData, succeeded and failed are recomputed. A nonexistent results directory, or one without raw.txt files, logs an error and `main` returns 1 without creating any directory. `main` returns 1 whenever it catches an exception (any mode).
2. `--type` choices are `all`, `datarate` only (`update` had no test type, KeyError).
3. `main(argv)` honours argv (`parse_args(argv[1:])`; default `sys.argv`).
4. `DockerHelper.benchmark` watch function uses an incremental UTF-8 decoder, flushed at the end, so multibyte characters split across chunks are not corrupted into U+FFFD.
5. `deployment/vagrant/bootstrap.sh` uses `"$HOME/.firstboot"` and touches it at the end of the block.
6. `github_actions_diff.py` uses `.splitlines()` (filenames with spaces).
7. `toolset/utils/scaffolding.py` continuation-line indentation re-aligned (cosmetic).

## Acceptance
`pytest -q` and `ruff check toolset tests` clean; new tests fail before the fix.

## Out of scope
`toolset/continuous/`; `run()`/`stop()`/labels in docker_helper.py (feature 004).
