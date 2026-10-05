# 006 Plan

- New `toolset/utils/summary.py`:
  - `build_rows(results, tests_metadata)`: `results` is the results.json dict (`rawData.datarate`, `succeeded/failed.datarate`, `frameworks`, optional `excluded`); `tests_metadata` maps name to language. Returns row dicts with the CSV keys.
  - `to_csv(rows)` uses `csv.DictWriter`; `to_markdown(rows, meta)` takes `meta` with name, environmentDescription, startTime, completionTime (epoch ms), git.
- `Results.write_summary()`: builds rows from `__to_jsonable()` plus languages from `benchmarker.tests` and `config.exclude`, writes both files, returns the Markdown. Called at the end of `parse()` and from `set_completion_time()` (so completion time is in the header). Errors are logged, never raised.
- `Benchmarker.run()` logs the returned Markdown after `set_completion_time()`.
- Excluded: names in `config.exclude`. Frameworks listed but in neither succeeded nor failed are `failed`.
- Risk: `parse()` calls write_summary before completion time is set; the second call in `set_completion_time` refreshes it.
