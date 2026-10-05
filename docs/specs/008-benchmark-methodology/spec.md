# 008 Benchmark Methodology

- **Data:** 2026-10-04
- **Status:** proposto — aguardando revisão
- **Repos afetados:** `ssgberk/benchmark-tool` (BT): toolset CLI, `DockerHelper`, `Results`, `summary.py`, `benchmark_test.sh`, the `ssgberk` launcher. `ssgberk/ssg-frameworks` (SF): two new `build.sh` markers. The marker contract is owned by SF `docs/specs/001-canonical-build-runner`, and Task 11 amends it.
- **Siblings:** `plan.md` (formats, schema, statistics, decisions), `tasks.md`. Related: SF `docs/specs/005-reference-site-design` (what is built), SF `docs/specs/006-layout-conformance` (what makes a build valid), BT `docs/specs/002-hyperfine-results` (base parser), BT `004-concurrent-safe-runs` (run ids, labels), BT `006-results-summary` (`summary.csv`/`summary.md`).

## Context

The toolset can now run one cell (`-nf`, `-cs`, `-mr`) for a set of generators and write `results/<ts>/results.json` and `summary.csv`/`summary.md` (BT 002, BT 006). It does not define a methodology:

| Gap | Today | Consequence |
|---|---|---|
| Which cells to run | `benchmark_test.sh` lists 7 cells with 10 runs each, plus `--clean` first | ad-hoc; deletes earlier results; nobody runs the same matrix twice |
| Resources | the container gets 95% of host RAM, all CPUs, no pinning | results depend on what else runs; generators that spawn workers per core are favoured differently on each host |
| Concurrency | BT 004 makes concurrent runs safe | two benchmarks on one host share CPUs, and both are wrong |
| Metrics | wall time only (mean, stddev, median, min, max, times) | no CPU time, memory, output size, or image build time |
| Noise | none | a 30% stddev run ranks like a 1% one |
| Environment | free-text `--results-environment` | results from a MacBook and a Linux server are mixed silently |
| Profiles | none | Core and Extended (005) would be mixed in one ranking |

This spec defines suites, profiles, metrics, the run protocol, statistics, the results schema additions and validity threats, and the toolset changes that implement them.

## Contract ownership

| Contract | Owner |
|---|---|
| Suite definitions, profile series, metric definitions, run protocol, noise rule, statistics, ranking rule, `results.json` additions, `summary.csv` additional columns, environment fingerprint | **this spec** (`plan.md`) |
| Marker strings printed by `build.sh` (including `SSGBERK_INPUT`/`SSGBERK_OUTPUT` drafted here, `SSGBERK_CONFORMANCE_*` and `SSGBERK_PROFILE_UNSUPPORTED` drafted by SF 006) | SF `docs/specs/001-canonical-build-runner/plan.md` |
| Base `summary.csv` columns and file layout | BT `docs/specs/006-results-summary` |
| Base parsing of `SSGBERK_RESULT_*` | BT `docs/specs/002-hyperfine-results` |
| Reference site and profiles' content | SF `docs/specs/005-reference-site-design` |

## Goals & success criteria

1. One command runs a named, versioned suite. *Measured by:* `./ssgberk --suite standard --profile core` runs its 5 cells × all generators sequentially and writes one `suite.json` plus one standard `results.json` per cell.
2. Comparable resources for every generator. *Measured by:* every `rawData.datarate[<fw>][0]` carries identical `resources` (CPUs, memory, cpuset), and a unit test asserts `DockerHelper.benchmark` passes `nano_cpus`, `mem_limit`, `memswap_limit` and `cpuset_cpus` to `containers.run`.
3. Richer metrics. *Measured by:* each successful result has `median`, `stddev`, `cv`, `user`, `system`, `peakRssBytes`, `inputBytes`, `outputFiles`, `outputBytes`, `postsPerSecond` and `inputMBPerSecond`; `imageBuild.<fw>.seconds` is present and never added to a build time.
4. Noise is visible. *Measured by:* a result with CV > 10% is re-run once with doubled runs (cap 10), and if the CV is still > 10% it carries `noisy: true` and is marked in `summary.md`.
5. Rankings only compare like with like. *Measured by:* `summary.md` and `suite-summary.md` rank only within one (suite, cell, profile, environment fingerprint, Extended feature set). A unit test with mixed inputs produces separate tables.
6. Backward compatibility. *Measured by:* a `results.json` written before this spec is still parsed by `--parse` and `summary.py`, and every key that existed before keeps its name, type and meaning (a schema test over the BT 002 fixture).

## Requirements

### Suites

- **R-1** Suites are data in `toolset/benchmark/suites.json`, validated on load. A suite has `name`, `version` (integer), `cells` (list of `{numberOfFiles, contentSize}`), `runs`, `cooldownSeconds` and `timeoutSeconds` per cell and generator.
- **R-2** These suites exist with exactly these cells:
  - `smoke`: nf 10, cs 0.500, runs 1.
  - `standard`: 5 cells, runs 5: nf ∈ {100, 1000, 10000} × cs 0.500, plus nf ∈ {100, 1000} × cs 500, that is (100, 0.500), (100, 500), (1000, 0.500), (1000, 500), (10000, 0.500). The cell (10000, 500) is not in `standard`.
  - `stress`: 4 cells, runs 3: (100000, 0.500), (10000, 500), (1000, 1000), (100, 5000). The cell (10000, 500) is 5.12 GB of markdown per run and lives here, where `timeout` and `oom` are expected outcomes.
  - `legacy-2019`: the seven active cells of the former `benchmark_test.sh`, runs 10, for historical comparison only and never ranked against the others.
- **R-3** `--suite <name>` runs every cell of the suite for every selected generator. Cells run in the order listed. Within a cell, generators run in the deterministic rotated order defined in `plan.md` ("Order"). `--suite` cannot be combined with `-nf`, `-cs` or `-mr` (usage error, exit 1).
- **R-4** Without `--suite`, `-nf`/`-cs`/`-mr` keep working as today and the result records `suite: null` (an ad-hoc run, never ranked against suite results).
- **R-5** `benchmark_test.sh` becomes a thin wrapper, `exec ./ssgberk --suite "${1:-standard}" "${@:2}"`. It no longer calls `--clean`.

### Profiles

- **R-6** `--profile core|extended` (default `core`) is passed to `build.sh` as env `profile`. Core and Extended results are separate series: separate result directories, separate summary tables, never ranked together.
- **R-7** A generator that prints `SSGBERK_PROFILE_UNSUPPORTED <profile>` (exit 3) is recorded under a new `unsupported.datarate` list, not `failed`.
- **R-8** Extended results record the generator's declared feature list (from `SSGBERK_CONFORMANCE_OK … features=`). Ranking groups Extended results by identical feature set.

### Metrics

- **R-9** Wall time comes from hyperfine (`mean`, `stddev`, `median`, `min`, `max`, `times`). The headline is `median`.
- **R-10** CPU time: hyperfine's `user` and `system` (mean seconds per run) are stored. Derived `cpuUtilization = (user + system) / mean` (cores used on average).
- **R-11** Peak memory: `peakRssBytes = max(memory_usage_byte)` from the hyperfine export. That is `getrusage(RUSAGE_CHILDREN).ru_maxrss`, the same quantity `/usr/bin/time -v` reports as "Maximum resident set size". The raw `memoryUsageBytes` list is stored too. Rationale and limits are in `plan.md` ("Peak RSS").
- **R-12** Output and input size: `build.sh` prints `SSGBERK_INPUT files=<n> bytes=<b>` after content generation and `SSGBERK_OUTPUT files=<n> bytes=<b>` after the verification build (sum of regular-file sizes; SF 001 contract, Task 11). The toolset stores `inputFiles`, `inputBytes`, `outputFiles` and `outputBytes`.
- **R-13** Throughput: `postsPerSecond = numberOfFiles / median` and `inputMBPerSecond = inputBytes / 10^6 / median`.
- **R-14** Image build: `DockerHelper.build` is timed with `time.monotonic()`, and the time is stored as `imageBuild.<fw>.seconds` together with `imageId`, `sizeBytes` and `noCache`. It is never added to, or reported in the same column as, build times.

### Protocol

- **R-15** Every timed run is a cold full rebuild. `build.sh` removes `output_folder` and `cache_folders` with hyperfine `--prepare` before each run (SF 001, unchanged). The toolset asserts that `SSGBERK_VERIFY_OK` and `SSGBERK_CONFORMANCE_OK` precede `STARTTIME`, and otherwise treats the result as failed.
- **R-16** The untimed verification build is the warm-up: it loads the generator's binaries, `node_modules` and gems into the OS page cache. Timed runs therefore measure "cold generator caches, warm OS page cache". hyperfine `--warmup` stays 0. The page cache is not dropped (no privileged containers).
- **R-17** Resources: the benchmark container runs with `--cpus` (default 4), `--memory` (default `8g`) with swap disabled (`memswap_limit = mem_limit`), and `--cpuset` (default `auto`, see `plan.md` "Resources"). Values are identical for every generator in a run and recorded in `resources`. `--cpus` greater than the Docker host's `NCPU` is a usage error.
- **R-18** Sequential execution: before benchmarking, the toolset lists running containers labelled `ssgberk.run` (BT 004). If any belong to another run id, it aborts with exit 1 and a message naming them, unless `--allow-concurrent` is given. In that case `protocol.concurrent` is `true` and summaries print "not ranked: concurrent run".
- **R-19** Timeouts and OOM: a container still running after `timeoutSeconds` is stopped, and the result status is `timeout`. A container whose state reports `OOMKilled` (or exit 137 with the memory limit reached) gets status `oom`. Both go to `failed.datarate` with `failureReasons.<fw>` set. They are not retried.
- **R-20** Environment capture into `results.json` `environment` (schema in `plan.md`): Docker `info()` and `version()` fields, CPU model (from the launcher's host probe, with the toolset container's `/proc/cpuinfo` as fallback), host OS (launcher), toolset git commit, Python and docker-py versions, per-generator image id, base image digest and generator version (from SF `generators.json` `generators[].version` when present, else the dockerfile `ARG <NAME>_VERSION`, else `null` with `versionSource: null`). Plus `environment.fingerprint`, defined in `plan.md`.
- **R-21** Noise control: `cv = stddev / mean`. If `runs ≥ 3` and `cv > 0.10`, the toolset re-runs that generator's cell once with `min_runs = min(2·runs, 10)`. The reported result is the last attempt. All attempts are kept in `attempts`. If the last attempt still has `cv > 0.10`, the result gets `noisy: true`.
- **R-22** Cool-down: the toolset sleeps `cooldownSeconds` (suite value; `smoke` 0, `standard` 15, `stress` 30) between generator runs.

### Statistics and reporting

- **R-23** Headline: `median` (seconds). Dispersion: `cv` (as %) and the `[min, max]` range.
- **R-24** Ranking: within one (suite name+version, cell, profile, fingerprint, Extended feature set), generators are ordered by median ascending. Adjacent generators whose `[min, max]` ranges overlap share a rank (shown as `=n`). Noisy results are ranked but marked. Results from different groups are never placed in one ranked table.
- **R-25** Scaling: for each (generator, cs) with ≥ 2 suite cells, `scaling.csv` has columns `framework,profile,contentSize,numberOfFiles,median`, and `suite-summary.md` shows the log-log slope `b` of `median ≈ a·nf^b` (least squares on log10), as "scaling exponent". It needs at least 3 points and is otherwise empty.
- **R-26** `summary.csv` (BT 006) gains these columns, appended after BT 006's columns in this order: `suite,suiteVersion,profile,features,fingerprint,cv,noisy,attempts,user,system,cpuUtilization,peakRssMB,inputMB,outputFiles,outputMB,postsPerSecond,inputMBPerSecond,imageBuildSeconds,failureReason`. `status` gains the values `timeout`, `oom`, `nonconformant` and `unsupported`. Rows keep BT 006's order rules, and `summary.md` gains matching columns plus a "Ranking" section per R-24.
- **R-27** A suite run writes `results/<ts>/suite.json`, `results/<ts>/suite-summary.csv`, `results/<ts>/suite-summary.md` and `results/<ts>/scaling.csv`, plus one standard per-cell directory `results/<ts>/<profile>/nf<nf>-cs<cs>/` holding `results.json`, `summary.csv`, `summary.md` and the per-generator raw files.

### Results schema

- **R-28** `results.json` additions are additive only. `schemaVersion: 2` is added at the top level, and its absence means version 1. Existing keys keep name, type and meaning. New keys are listed in `plan.md` ("Results schema additions"). Readers treat every new key as optional.

### Parsing (toolset side of SF markers)

- **R-29** `Results.parse_build_output` additionally: treats `SSGBERK_CONFORMANCE_FAIL` like `SSGBERK_VERIFY_FAIL` (returns `[]`, failure reason `nonconformant: <first fail line>`); treats `SSGBERK_PROFILE_UNSUPPORTED` as status `unsupported`; reads `user`, `system` and `memory_usage_byte` from the hyperfine result; reads `SSGBERK_INPUT`/`SSGBERK_OUTPUT`; and reads `features=` from `SSGBERK_CONFORMANCE_OK`. A missing optional marker leaves the field `null` without failing.

### Validity threats

- **R-30** `plan.md` ("Validity threats") lists every known threat with its mitigation and whether it is reported. `summary.md` prints a fixed caveat block when the environment is Docker Desktop (`docker.operatingSystem` contains `Docker Desktop`) or when any result is noisy, concurrent or from `legacy-2019`.

## Out of scope

- A results website or charts (BT 006 Out of scope stands).
- Statistical significance tests (bootstrap CIs, Mann–Whitney). Range overlap is the tie rule. See Open questions.
- Dropping the OS page cache, CPU frequency governors, disabling turbo/SMT. These are host tuning, documented as threats, not automated.
- Incremental or watch-mode build benchmarks.
- Changing what the reference site contains (SF 005) or how conformance is decided (SF 006).

## Decisions log

Decided by the maintainer on 2026-10-04:

1. **Suite cells.** (10000, 500) moves out of `standard` and into `stress`. `standard` has 5 cells: {100, 1000, 10000} × cs 0.500 plus {100, 1000} × cs 500. `stress` has 4 cells: (100000, 0.500), (10000, 500), (1000, 1000), (100, 5000). *Decided by the maintainer, 2026-10-04.*
2. **Peak RSS source.** `peakRssBytes` comes from hyperfine 1.20 `memory_usage_byte` (`ru_maxrss`, `getrusage(RUSAGE_CHILDREN)`), not from `/usr/bin/time -v` or cgroup `memory.peak`. Limits (running maximum, largest single process) stay in `plan.md` "Peak RSS" and threat T7. *Decided by the maintainer, 2026-10-04.*
3. **Default container resources.** `--cpus 4 --memory 8g`. *Decided by the maintainer, 2026-10-04.*

Decided by the maintainer on 2026-10-05:

4. **2026-10-05 — site-size scenarios P/M/G/GG at 5 and 50 KB, decided by the maintainer.** Four suites model real site sizes, each with 2 cells at 5 KB and 50 KB per page: P (website pessoal, 50 pages), M (site corporativo, 1,000), G (grande portal, 10,000) and GG (portal massivo, 100,000). `-cs` accepts two new values, `5` and `50`. The canonical `build.sh` gets the matching mapping in ssg-frameworks spec 005: `5` = 10 blocks, `50` = 100 blocks. *Decided by the maintainer, 2026-10-05.*

## Open questions

1. **Tie rule.** Overlap of `[min, max]` is crude with 5 runs, but it is transparent. A bootstrap CI of the median would be better but adds complexity to `summary.py`. Proposal: keep overlap now and revisit after the first `standard` round.
2. **CPU model on Docker Desktop.** Inside the Linux VM `/proc/cpuinfo` has no model name on Apple silicon, so the launcher probe (`sysctl -n machdep.cpu.brand_string` on macOS, `lscpu` on Linux) is the primary source. If the toolset runs without the launcher (CI calling `run-tests.py` directly), only the fallback is available.
3. **Dependence on unmerged specs.** Run ids and labels (BT 004) and `summary.py` (BT 006) are on `feat/004-concurrent-safe-runs` and `feat/006-results-summary`. Tasks 5 and 10 assume both are merged first.
