# Plan
- `toolset/utils/benchmark_config.py`: add `run_id`; claim a unique results dir for non-parse runs.
- `toolset/utils/results.py`: `self.uuid = self.config.run_id` (fallback to uuid4 if absent).
- `toolset/utils/docker_helper.py`: `RUN_LABEL`; `labels` + unique `name` in `run()`; `labels` in `benchmark()`; `__stop_all` lists with label filter, tolerating NotFound/ImageNotFound; `stop()` prunes only when appropriate (prune removes only stopped containers, left as is).
- Tests: `tests/test_docker_helper.py`, new `tests/test_benchmark_config.py`.
Risk: `containers.prune()` is global but only removes stopped containers (run containers use `remove=True`); kept.
