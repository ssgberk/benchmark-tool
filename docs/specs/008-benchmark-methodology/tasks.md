# 008 Benchmark Methodology — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run named suites under a fixed, recorded protocol: profiles as separate series, fixed container resources, sequential execution, environment capture, CPU, memory and output metrics, noise control, and like-for-like rankings. Every change to `results.json` is backward compatible.

**Architecture:** Suites are data (`toolset/benchmark/suites.json`) expanded by `toolset/benchmark/suites.py`. `run-tests.py` loops over the cells, one `Benchmarker` per cell, writing standard per-cell result directories plus a suite index. `DockerHelper.benchmark` applies resource limits and detects timeouts and OOM. `Results.parse_build_output` reads the new hyperfine fields and SF markers. `toolset/utils/environment.py` captures the environment and fingerprint. `summary.py` (BT 006) gains the 008 columns, ranking and scaling. Formats are in `plan.md`.

**Tech Stack:** Python 3.12, docker-py 7.1.0, pytest, ruff, hyperfine 1.20.0 (in generator images), bash (launcher).

**Spec:** `docs/specs/008-benchmark-methodology/spec.md` and `plan.md` (repo `ssgberk/benchmark-tool`). Read both before starting any task.

In this file **BT** = `/Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize` (repo `ssgberk/benchmark-tool`, branch `chore/modernize-2026`) and **SF** = `BT/frameworks` (repo `ssgberk/ssg-frameworks`, branch `chore/modernize-2026`). Layout: `docs/specs/ROADMAP.md` in BT.

Prerequisites: BT 002 done. Tasks 5 and 10 also need BT 004 (`feat/004-concurrent-safe-runs`) and BT 006 (`feat/006-results-summary`) merged. Tasks 2–3 are exercised end to end only after SF 006 Task 9 (`profile` env, conformance markers). Their unit tests use fixtures and do not wait for it.

## Global Constraints

- Git author/committer `Matheus Breguêz <matbrgz@gmail.com>`; every commit GPG-signed (repo config already has `commit.gpgsign=true`, key `B6FA8458D5176E83`). Never use `--no-gpg-sign` or `--author`.
- Every commit message ends with the trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Never commit to `master`. Never push, open PRs, or close dependabot branches unless the human explicitly asks.
- Markers consumed (owned by SF `docs/specs/001-canonical-build-runner`): `SSGBERK_RESULT_BEGIN`, `SSGBERK_RESULT_END`, `SSGBERK_VERIFY_OK`, `SSGBERK_VERIFY_FAIL`, `SSGBERK_CONFORMANCE_OK`, `SSGBERK_CONFORMANCE_FAIL`, `SSGBERK_PROFILE_UNSUPPORTED`, `SSGBERK_INPUT`, `SSGBERK_OUTPUT`, `STARTTIME <epoch>`, `ENDTIME <epoch>`. They are repeated here because the tests use them.
- `results.json` changes are additive only (spec R-28). Never rename or retype an existing key.
- Unit tests never need Docker: mock `docker.DockerClient` as `tests/test_docker_helper.py` does.
- `pytest -q` and `ruff check toolset tests` are clean after every task.
- Never run two benchmark runs at once on the same machine (the guard of Task 5 enforces this from then on).

## Review Focus

1. **Silent breakage of old readers.** Pinned by `test_v1_results_still_parse` (Task 9) over `tests/fixtures/results_v1.json`.
2. **Resource limits not applied.** Pinned by `test_benchmark_passes_resource_limits` (Task 4).
3. **Cherry-picking attempts.** The reported attempt must be the last one, not the best. Pinned by `test_rerun_reports_last_attempt` (Task 6).
4. **Ranking across groups.** Pinned by `test_ranking_never_mixes_groups` (Task 10).

---

### Task 1: Suite definitions and `--suite`

**Files:**
- Create: `toolset/benchmark/suites.json`, `toolset/benchmark/suites.py`, `tests/test_suites.py`
- Modify: `toolset/run-tests.py` (`--suite`; the cell loop), `toolset/utils/benchmark_config.py` (per-cell copy: `number_of_files`, `content_size`, `min_runs`, `suite`, `cell_index`, `timestamp` subdir), `benchmark_test.sh`, `README.md` (usage)

**Interfaces:**
- `suites.load(name: str, path=DEFAULT) -> Suite` with `Suite(name, version, runs, cooldown_seconds, timeout_seconds, ranked, cells: list[Cell])` and `Cell(number_of_files: int, content_size: str)`. Raises `SuiteError` on unknown name or invalid data.
- `suites.cell_dir(profile, cell) -> str` returns `"<profile>/nf<nf>-cs<cs>"`.
- `suites.rotate(names: list[str], cell_index: int) -> list[str]` (plan "Order").
- `run-tests.py`: `--suite NAME` (choices from `suites.json`). Combining it with an explicit `-nf`, `-cs` or `-mr` is a usage error with exit 1.

- [ ] **Step 1: Write the failing test** — `tests/test_suites.py`: `test_standard_cells` (exactly the 5 cells and runs 5 of plan "Suites", and `(10000, "500")` absent); `test_smoke`, `test_stress` (exactly 4 cells, including `(10000, "500")`, runs 3), `test_legacy_2019` (7 cells, runs 10, `ranked` false); `test_invalid_content_size_rejected`; `test_unknown_suite`; `test_cell_dir` (`core/nf1000-cs0.500`); `test_rotate_deterministic` (same output twice, cell 0 = sorted, cell 1 rotated by 7 mod n); `test_suite_conflicts_with_nf` (`main(['x', '--suite', 'smoke', '-nf', '5'])` returns 1); `test_benchmark_test_sh_is_wrapper` (the file contains `--suite` and not `--clean`).
- [ ] **Step 2: Run** `pytest -q tests/test_suites.py` → FAIL.
- [ ] **Step 3: Implement.** `run-tests.py` main: if `--suite`, then for each cell build a per-cell `BenchmarkConfig` (copy of args with the cell values, `results` dir `results/<ts>/<cell_dir>`) and a `Benchmarker`, and run it. After the loop, write `suite.json` (plan "`suite.json`"). `benchmark_test.sh` becomes `#!/bin/bash` + a comment + `exec ./ssgberk --suite "${1:-standard}" "${@:2}"`.
- [ ] **Step 4: Run** → PASS; `pytest -q` and `ruff check toolset tests` clean.
- [ ] **Step 5: Commit** `feat(toolset): named benchmark suites (--suite)`.

### Task 2: Profiles as separate series

**Files:**
- Modify: `toolset/run-tests.py` (`--profile core|extended`), `toolset/utils/benchmark_config.py` (`profile`), `toolset/benchmark/test_types/datarate_type.py` (`get_script_variables` adds `profile`), `toolset/utils/results.py` (`profile` top-level; `unsupported.datarate`)
- Test: `tests/test_cli.py`, `tests/test_results.py`

**Interfaces:**
- Env passed to `build.sh`: `profile=<core|extended>` (SF 006 Task 9 consumes it).
- Results: top-level `profile`; `unsupported = {"datarate": [names]}`.

- [ ] **Step 1: Write the failing test** — `test_profile_default_core`, `test_profile_passed_to_script_variables` (`DatarateTestType(config).get_script_variables()['profile'] == 'extended'`), `test_results_dir_includes_profile_for_suite` (`results/<ts>/extended/nf10-cs0.500`), `test_unsupported_recorded_not_failed` (a raw fixture with `SSGBERK_PROFILE_UNSUPPORTED extended` puts the framework in `unsupported.datarate` and not in `failed.datarate`).
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.** `report_benchmark_results` routes unsupported results using the status from Task 3's parser. Until Task 3 lands, detect the marker with a simple `in` check, which Task 3 replaces.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(toolset): --profile core|extended as separate result series`.

### Task 3: Parser for new metrics and markers

**Files:**
- Modify: `toolset/utils/results.py` (`parse_build_output`, `parse_test`, `report_benchmark_results`, `failureReasons`)
- Create: `tests/fixtures/raw_v2_ok.txt` (hyperfine JSON with `user`, `system`, `memory_usage_byte`; `SSGBERK_INPUT`, `SSGBERK_VERIFY_OK`, `SSGBERK_CONFORMANCE_OK profile=core posts=10 sampled=10 features=-`, `SSGBERK_OUTPUT`), `tests/fixtures/raw_conformance_fail.txt`, `tests/fixtures/raw_unsupported.txt`
- Test: `tests/test_results.py`

**Interfaces:**
- `parse_build_output(text, number_of_files, content_size, min_runs) -> list[dict]`. The success dict adds `user`, `system`, `cpuUtilization`, `memoryUsageBytes`, `peakRssBytes`, `inputFiles`, `inputBytes`, `outputFiles`, `outputBytes`, `cv`, `postsPerSecond`, `inputMBPerSecond`, `features`, `status: "ok"` (plan "Results schema additions"; missing optional markers give `null`).
- New `classify_build_output(text) -> tuple[str, str | None]` returns `(status, reason)`: `("nonconformant", "<first SSGBERK_CONFORMANCE_FAIL line>")`, `("failed", "<first SSGBERK_VERIFY_FAIL line>")`, `("unsupported", None)` or `("ok", None)`. A result whose `SSGBERK_VERIFY_OK`/`SSGBERK_CONFORMANCE_OK` do not both precede `STARTTIME` is `("failed", "protocol: verification markers missing before STARTTIME")` (spec R-15). `classify_build_output(text, require_conformance=False)`: with the new `--require-conformance` switch (default off, threaded through `BenchmarkConfig`; SF 006 Task 27 flips the default on) a missing `SSGBERK_CONFORMANCE_OK` is `("nonconformant", "nonconformant: missing SSGBERK_CONFORMANCE_OK")`. With it off, a missing marker is tolerated when the text contains no `SSGBERK_CONFORMANCE_` line at all; the reason is `null` and the result records `conformance: "unchecked"` (`"ok"` otherwise). Conformance failure reasons are `nonconformant: <line>` (R-29).

- [ ] **Step 1: Write the failing test** — `test_v2_fields` (values from `raw_v2_ok.txt`: `peakRssBytes == max(memory_usage_byte)`, `cpuUtilization == round((user+system)/mean, 3)`, `postsPerSecond == nf/median`, `inputMBPerSecond == inputBytes/1e6/median`, `cv == stddev/mean`); `test_v1_raw_still_parses` (the existing `tests/fixtures/raw_ok.txt` gives a result with new keys `null` and old keys unchanged); `test_conformance_fail_is_failed_with_reason`; `test_unsupported_status`; `test_verify_ok_must_precede_starttime`; `test_cv_null_for_single_run`.
- [ ] **Step 2: Run** `pytest -q tests/test_results.py` → FAIL.
- [ ] **Step 3: Implement.** Store `failureReasons[<fw>]` in `report_benchmark_results` and emit it in `__to_jsonable`.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(results): parse cpu, memory, io metrics and conformance markers`.

### Task 4: Resource limits, timeout and OOM in `DockerHelper.benchmark`

**Files:**
- Modify: `toolset/utils/docker_helper.py` (`benchmark`; drop the module-level 95% `mem_limit` for benchmark containers), `toolset/run-tests.py` (`--cpus`, `--memory`, `--cpuset`), `toolset/utils/benchmark_config.py`
- Create: `toolset/utils/resources.py`
- Test: `tests/test_docker_helper.py`, `tests/test_resources.py`

**Interfaces:**
- `resources.parse_memory("8g") -> int` (accepts `k`, `m`, `g` suffixes, base 1024); `resources.resolve(cpus: float, memory: int, cpuset: str, ncpu: int) -> dict` returns `{"cpus", "memoryBytes", "swap": False, "cpuset"}` (plan "Resources"; raises `ValueError` when `cpus > ncpu` or the cpuset is out of range).
- `DockerHelper.benchmark(framework_test, script, variables, raw_file, resources: dict, timeout_seconds: int) -> dict` returns `{"status": "ok"|"timeout"|"oom", "exitCode": int}`. It runs with `detach=True`, `remove=False`, `nano_cpus`, `mem_limit`, `memswap_limit`, `cpuset_cpus`, streams logs (unchanged verbatim writing), `wait(timeout=…)`, and on timeout `stop()` → `"timeout"`. Otherwise it inspects `State.OOMKilled` → `"oom"`, and finally `remove(force=True)`.

- [ ] **Step 1: Write the failing test** — `test_resolve_auto_cpuset` (`ncpu=8, cpus=4` → `"4-7"`; `ncpu=4, cpus=4` → `None`); `test_resolve_rejects_too_many_cpus`; `test_parse_memory`; `test_benchmark_passes_resource_limits` (mock `containers.run` asserts `nano_cpus=4_000_000_000`, `mem_limit == memswap_limit == 8589934592`, `cpuset_cpus="4-7"`, `remove=False`); `test_benchmark_timeout` (mock `wait` raises `requests.exceptions.ReadTimeout` → `status == "timeout"`, `stop` called); `test_benchmark_oom` (`attrs['State']['OOMKilled'] = True` → `"oom"`); `test_container_removed_after_inspect`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.** The benchmarker passes the run's resolved resources to every call and writes `resources` to results. Status `timeout`/`oom` goes to `failed.datarate` with `failureReasons`.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(docker): fixed cpu/memory/cpuset limits, timeout and oom detection`.

### Task 5: Sequential-execution guard

Needs BT 004 merged (labels `ssgberk.run=<run_id>`).

**Files:**
- Modify: `toolset/benchmark/benchmarker.py` (`run`: guard before the first test), `toolset/run-tests.py` (`--allow-concurrent`), `toolset/utils/results.py` (`protocol`)
- Test: `tests/test_benchmarker_guard.py`

**Interfaces:**
- `DockerHelper.other_runs(own_run_id) -> list[str]` returns run ids from `containers.list(filters={"label": "ssgberk.run"})` whose label differs from `own_run_id`. `NotFound` is tolerated.
- `protocol = {"coldRebuild": true, "warmupBuilds": 1, "sequential": not concurrent, "concurrent": bool, "cooldownSeconds", "timeoutSeconds", "cvThreshold": 0.10}`.

- [ ] **Step 1: Write the failing test** — `test_guard_aborts_on_other_run` (`run()` returns failure and logs the other run id; no test is started); `test_allow_concurrent_records_flag` (`protocol.concurrent is True`); `test_guard_ignores_own_run`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(toolset): refuse concurrent benchmark runs unless --allow-concurrent`.

### Task 6: Noise control (CV re-run) and cool-down

**Files:**
- Modify: `toolset/benchmark/benchmarker.py` (`__benchmark`: re-run logic, cool-down sleep), `toolset/benchmark/test_types/datarate_type.py` (`min_runs` override per attempt)
- Create: `toolset/benchmark/noise.py`
- Test: `tests/test_noise.py`

**Interfaces:**
- `noise.needs_rerun(result: dict, runs: int, threshold=0.10) -> bool` (true if `runs ≥ 3` and `cv > threshold`); `noise.rerun_runs(runs) -> int` returns `min(2 * runs, 10)`; `noise.finalize(attempts: list[dict], threshold) -> dict` returns the last attempt plus `attempts` (summaries of all) and `noisy` (last `cv > threshold`).

- [ ] **Step 1: Write the failing test** — `test_no_rerun_below_threshold`; `test_no_rerun_single_run`; `test_rerun_runs_capped` (5 → 10, 8 → 10, 3 → 6); `test_rerun_reports_last_attempt` (attempts with cv 0.15 then 0.12 → the reported result is attempt 2 with `noisy` true; attempts with cv 0.15 then 0.04 → attempt 2 with `noisy` false; never the lower-cv attempt when it is not last); `test_benchmarker_reruns_once` (mocked `docker_helper.benchmark` and parser: a first result with cv 0.2 triggers exactly one more call with `min_runs` 10, never a third); `test_cooldown_sleep_called_between_tests` (patch `time.sleep`).
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.** The re-run overwrites `raw.txt`, and the first attempt's raw output is kept as `raw.attempt1.txt`.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(toolset): cv-based re-run and noisy flag`.

### Task 7: Environment capture and fingerprint

**Files:**
- Create: `toolset/utils/environment.py`, `tests/test_environment.py`, `tests/fixtures/docker_info.json`, `tests/fixtures/docker_version.json`, `tests/fixtures/generators.json`
- Modify: `toolset/utils/results.py` (`environment`, `generators`), `ssgberk` (launcher passes `-e SSGBERK_HOST_CPU -e SSGBERK_HOST_OS`)

**Interfaces:**
- `environment.capture(docker_client, resources, toolset_commit, env=os.environ, cpuinfo_path="/proc/cpuinfo") -> dict` (plan "Results schema additions" `environment`). `cpuModel` comes from `SSGBERK_HOST_CPU` (`cpuModelSource: "launcher"`), else the `model name` in `/proc/cpuinfo` (`"cpuinfo"`), else `null`.
- `environment.fingerprint(env: dict, resources: dict) -> str` (12 hex; plan definition).
- `environment.generator_versions(fw_root, names) -> dict`, reading `frameworks/generators.json` `generators[].{id,version}` when present (`versionSource: "generators.json"`), else the first `ARG <NAME>_VERSION=<v>` in `<name>.dockerfile` (`"dockerfile-arg"`), else `null`.
- Launcher: `SSGBERK_HOST_CPU="$( (sysctl -n machdep.cpu.brand_string 2>/dev/null || lscpu 2>/dev/null | sed -n 's/^Model name:[[:space:]]*//p') | head -1)"`, `SSGBERK_HOST_OS="$(uname -srm)"`.

- [ ] **Step 1: Write the failing test** — `test_capture_from_fixtures` (all docker fields mapped; missing keys give `null`); `test_cpu_model_precedence` (launcher > cpuinfo > null); `test_fingerprint_stable_and_sensitive` (same inputs give the same value; changing `resources.cpus` changes it; changing `toolset.commit` does not); `test_generator_versions_prefers_generators_json`; `test_generator_versions_dockerfile_fallback` (`ARG HUGO_VERSION=0.167.0`); `test_launcher_exports_host_env` (grep the `ssgberk` script for both `-e` flags).
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.** Image ids come from `docker_client.images.get("ssgberk/test.<name>").id`; the base digest from `images.get("ubuntu:24.04").attrs["RepoDigests"][0]` when present.
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(results): capture environment, fingerprint and generator versions`.

### Task 8: Image build time, recorded separately

**Files:**
- Modify: `toolset/utils/docker_helper.py` (`build`: time it with `time.monotonic()`; return the seconds through a new attribute), `toolset/benchmark/framework_test.py` (store it on the test), `toolset/utils/results.py` (`imageBuild`), `toolset/run-tests.py` (`--no-cache` passes `nocache=True` to the build)
- Test: `tests/test_docker_helper.py`, `tests/test_results.py`

**Interfaces:**
- `DockerHelper.build(test, build_log_dir) -> int` (unchanged return) and `DockerHelper.last_build = {"seconds": float, "imageId": str|None, "sizeBytes": int|None, "noCache": bool}`.
- `results.json` `imageBuild.<fw>` uses the same shape.

- [ ] **Step 1: Write the failing test** — `test_build_records_seconds` (patch `time.monotonic` → 10.0, 52.5 gives `seconds == 42.5`); `test_image_build_not_in_rawdata` (the result dict for the framework has no `imageBuild`/`seconds` keys and `mean` is unchanged); `test_no_cache_flag_passed`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(results): record image build time separately from build time`.

### Task 9: Results schema version 2 and backward compatibility

**Files:**
- Modify: `toolset/utils/results.py` (`__to_jsonable`: `schemaVersion`, `suite`, `profile`, `resources`, `protocol`, `environment`, `generators`, `imageBuild`, `unsupported`, `failureReasons`; `load()` tolerates their absence)
- Create: `tests/fixtures/results_v1.json` (a real pre-008 `results.json`), `tests/test_schema.py`

**Interfaces:**
- Reader rule: every key added by 008 is optional. `schemaVersion` absent means 1.

- [ ] **Step 1: Write the failing test** — `test_v2_top_level_keys` (a full run with mocks writes all plan keys with the documented types); `test_v1_results_still_parse` (`--parse` over a dir holding `results_v1.json` and raw files completes, and the old keys keep their values and types); `test_old_keys_unchanged` (set equality: v1 keys ⊆ v2 keys, with identical types for the fixture values).
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(results): schemaVersion 2 with additive methodology keys`.

### Task 10: Summary columns, ranking, scaling and suite summary

Needs BT 006 merged (`toolset/utils/summary.py`).

**Files:**
- Modify: `toolset/utils/summary.py` (`build_rows`, `to_csv`, `to_markdown`), `toolset/utils/results.py` (`write_summary`)
- Create: `toolset/utils/ranking.py`, `tests/test_ranking.py`, `tests/test_summary_008.py`, `tests/fixtures/suite_standard/` (5 cells × 3 frameworks of synthetic `results.json`)
- Modify: `toolset/run-tests.py` (after a suite: `suite-summary.csv`, `suite-summary.md`, `scaling.csv`)

**Interfaces:**
- `ranking.group_key(result_meta, row) -> tuple` returns `(suite, suiteVersion, numberOfFiles, contentSize, profile, fingerprint, features)`.
- `ranking.rank(rows) -> list[str]` returns rank labels (`"1"`, `"=1"`, …) by the plan overlap rule.
- `ranking.scaling_exponent(points: list[tuple[int, float]]) -> float | None` (`None` below 3 points).
- `summary.csv` columns: BT 006 columns + spec R-26 columns in that order.

- [ ] **Step 1: Write the failing test** — `test_csv_columns_order` (header equals BT 006 + R-26 list); `test_status_values` (`timeout`, `oom`, `nonconformant` and `unsupported` rows have empty numbers); `test_rank_overlap_ties` (min–max overlap gives `=1`); `test_ranking_never_mixes_groups` (two fingerprints give two tables); `test_legacy_not_ranked` (`ranked: false` gives no Rank column values); `test_scaling_exponent_linear` (points `(100, 1), (1000, 10), (10000, 100)` → `1.00`); `test_scaling_needs_three_points`; `test_caveat_block_docker_desktop` (`operatingSystem: "Docker Desktop"` gives the T1 caveat text); `test_noisy_marker` (` ⚠` suffix); `test_suite_summary_files_written`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** per plan "Statistics" and "`summary.md` additions".
- [ ] **Step 4: Run** → PASS.
- [ ] **Step 5: Commit** `feat(summary): methodology columns, ranking groups and scaling exponent`.

### Task 11: SF-side markers `SSGBERK_INPUT` / `SSGBERK_OUTPUT` (cross-repo)

This task changes SF, because `build.sh` and its marker contract are owned by SF `docs/specs/001-canonical-build-runner`. Run it in SF.

**Files (SF):**
- Modify: `docs/specs/001-canonical-build-runner/plan.md` (marker table: the two rows from this plan's "Marker drafts for SF 001"), `Go/hugo/build.sh` (snippet from the same section; then copy to every `*/*/build.sh`), `tests/build_sh/test_build_sh.sh`

**Interfaces:**
- Produces: `SSGBERK_INPUT files=<n> bytes=<b>` after content generation; `SSGBERK_OUTPUT files=<n> bytes=<b>` after the conformance check and before `STARTTIME`.

- [ ] **Step 1: Write the failing test** — in SF `tests/build_sh/test_build_sh.sh`: `test_input_marker` (N=3, `-cs 0.500`, `type: none` → `SSGBERK_INPUT files=3 bytes=1536`); `test_output_marker` (the fake generator writes 2 files of 10 bytes → `SSGBERK_OUTPUT files=2 bytes=20`); `test_markers_before_starttime`.
- [ ] **Step 2: Run** `bash tests/build_sh/test_build_sh.sh` in SF → FAIL.
- [ ] **Step 3: Implement** and propagate `build.sh` to all generators; `tools/check-build-sh.sh` exits 0.
- [ ] **Step 4: Run** → PASS; smoke one generator from BT (`./ssgberk --test hugo -nf 10 -cs 0.500 -mr 1`) and check the parsed `inputBytes`/`outputBytes` in `results.json`.
- [ ] **Step 5: Commit (SF)** `feat(build.sh): print input and output size markers (BT 008)`.

### Task 12: Methodology documentation

**Files:**
- Modify: `README.md` (section "Methodology": suites, profiles, protocol, metrics, how to read rankings, validity threats; links to this spec), `docs/specs/ROADMAP.md` (008 execution step)

**Interfaces:**
- None (docs).

- [ ] **Step 1: Write the failing check** — `grep -c "## Methodology" README.md` prints `0`.
- [ ] **Step 2: Run** → `0`.
- [ ] **Step 3: Implement** — README section with: the suite table (from plan), `./ssgberk --suite standard --profile core` example, resource defaults, what "cold rebuild, warm OS cache" means, the headline median plus CV and range, the ranking rule, and the threats list (T1–T11, one line each). ROADMAP: add step "8. BT 008-benchmark-methodology (needs BT 002, BT 004, BT 006, SF 006 Task 9)".
- [ ] **Step 4: Run** → `grep -c "## Methodology" README.md` prints `1`; `grep -c "008-benchmark-methodology" docs/specs/ROADMAP.md` ≥ 2.
- [ ] **Step 5: Commit** `docs: benchmark methodology section`.
