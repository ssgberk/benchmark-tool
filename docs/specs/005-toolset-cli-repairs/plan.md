# 005 Plan
Files: `toolset/run-tests.py`, `toolset/utils/docker_helper.py` (only `benchmark().watch_container`, with a function-local `import codecs` to avoid import-block merge conflicts with 004), `toolset/utils/scaffolding.py`, `toolset/github_actions/github_actions_diff.py`, `deployment/vagrant/bootstrap.sh`, tests in `tests/test_cli.py`, `tests/test_docker_helper.py`, `tests/test_github_actions_diff.py`.
Risk: `main()` still swallows exceptions inside its try block; the parse test asserts on results.json content, not return code.

Fix round 1: `--parse` validates `FWROOT/results/<ts>/*/*/raw.txt` in run-tests.py BEFORE constructing BenchmarkConfig/Benchmarker (which create the dir), then `Results.load()`, resets rawData/succeeded/failed, re-parses. `main` returns 1 from its exception handler.
