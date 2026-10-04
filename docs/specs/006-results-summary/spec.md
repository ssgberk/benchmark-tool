# 006 Results Summary

- **Repo:** `ssgberk/benchmark-tool`
- **Status:** implementing

## Why
A run only leaves a raw `results.json`. The project exists to compare generators, so each run should also leave a human-readable comparison.

## Requirements
1. After a benchmark run and after `--parse`, write `results/<ts>/summary.csv` and `results/<ts>/summary.md`.
2. `summary.csv` columns: `framework,language,numberOfFiles,contentSize,minRuns,mean,stddev,median,min,max,status`. One row per generator. `status` is `ok`, `failed` or `excluded`; failed/excluded rows have empty numbers. Rows are sorted by mean ascending, then failed, then excluded rows (alphabetical within a group).
3. `summary.md`: header (run name, environment, start and completion time, git commit if present), a table with the same data (seconds with 3 decimals, `—` for a null stddev), then a "Failed" list.
4. `Benchmarker.run()` logs the Markdown table at the end.
5. Language comes from `FrameworkTest.language`; empty if unavailable.
6. Logic lives in `toolset/utils/summary.py` as pure functions `build_rows`, `to_csv`, `to_markdown`. Stdlib only.

## Acceptance
- Unit tests (no docker) cover ordering, failed/excluded rows, null stddev, CSV round-trip via `csv.DictReader`, Markdown header and row count.
- Hooked in `Results.parse()` and `set_completion_time()` path via `Results.write_summary()`; `run-tests.py` untouched.

## Out of scope
Charts, HTML, multi-run comparison, changes to `run-tests.py`.
