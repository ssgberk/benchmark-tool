# 008 Benchmark Methodology — Plan

Spec: `spec.md`. Tasks: `tasks.md`. This plan owns suites, the run protocol, metric definitions, statistics, the ranking rule, the `results.json` additions, the extra `summary.csv` columns and the environment fingerprint. Marker strings are owned by SF `docs/specs/001-canonical-build-runner/plan.md`. The two new ones are drafted under "Marker drafts for SF 001", and Task 11 moves them there.

Depends on: BT 002 (parser), BT 004 (run id, `ssgberk.run` label, results dir claim; branch `feat/004-concurrent-safe-runs`), BT 006 (`toolset/utils/summary.py`; branch `feat/006-results-summary`), SF 006 Task 9 (`profile` env, `SSGBERK_CONFORMANCE_*`).

## Architecture

```
./ssgberk --suite standard --profile core --cpus 4 --memory 8g
  launcher (host): probes CPU model / OS → env SSGBERK_HOST_CPU, SSGBERK_HOST_OS → toolset container
  run-tests.py
    ├─ suites.load("standard") → cells [(100,0.500),(100,500),(1000,0.500),(1000,500),(10000,0.500)], runs 5
    ├─ concurrency guard (labels, BT 004)               ── abort unless --allow-concurrent
    ├─ environment.capture(docker) → environment{…, fingerprint}
    └─ for cell in cells:                                 results/<ts>/<profile>/nf<nf>-cs<cs>/
         Benchmarker(config for cell).run()
           for test in rotated(tests, cell_index):
             DockerHelper.build (timed → imageBuild.<fw>)
             DockerHelper.benchmark(nano_cpus, mem_limit, memswap_limit, cpuset_cpus, timeout)
               build.sh (SF): generate → SSGBERK_INPUT → verify → SSGBERK_VERIFY_OK → conformance
                              → SSGBERK_CONFORMANCE_OK → SSGBERK_OUTPUT → STARTTIME → hyperfine → markers
             Results.parse_test → metrics; CV > 10% → one re-run with 2× runs (cap 10)
             sleep cooldownSeconds
         Results.parse → results.json (schemaVersion 2) + summary.csv/md (BT 006 + 008 columns)
    └─ suite.json, suite-summary.csv/md, scaling.csv in results/<ts>/
```

## Suites — `toolset/benchmark/suites.json`

```json
{
  "smoke": {
    "version": 1, "runs": 1, "cooldownSeconds": 0, "timeoutSeconds": 1800,
    "cells": [{"numberOfFiles": 10, "contentSize": "0.500"}]
  },
  "standard": {
    "version": 1, "runs": 5, "cooldownSeconds": 15, "timeoutSeconds": 7200,
    "cells": [
      {"numberOfFiles": 100,   "contentSize": "0.500"},
      {"numberOfFiles": 100,   "contentSize": "500"},
      {"numberOfFiles": 1000,  "contentSize": "0.500"},
      {"numberOfFiles": 1000,  "contentSize": "500"},
      {"numberOfFiles": 10000, "contentSize": "0.500"}
    ]
  },
  "stress": {
    "version": 1, "runs": 3, "cooldownSeconds": 30, "timeoutSeconds": 14400,
    "cells": [
      {"numberOfFiles": 100000, "contentSize": "0.500"},
      {"numberOfFiles": 10000,  "contentSize": "500"},
      {"numberOfFiles": 1000,   "contentSize": "1000"},
      {"numberOfFiles": 100,    "contentSize": "5000"}
    ]
  },
  "legacy-2019": {
    "version": 1, "runs": 10, "cooldownSeconds": 15, "timeoutSeconds": 7200, "ranked": false,
    "cells": [
      {"numberOfFiles": 10,     "contentSize": "0.500"},
      {"numberOfFiles": 100,    "contentSize": "0.500"},
      {"numberOfFiles": 1000,   "contentSize": "0.500"},
      {"numberOfFiles": 10000,  "contentSize": "0.500"},
      {"numberOfFiles": 10,     "contentSize": "1000"},
      {"numberOfFiles": 10,     "contentSize": "5000"},
      {"numberOfFiles": 100000, "contentSize": "0.500"}
    ]
  }
}
```

Validation (`suites.load`): every `contentSize` is one of the toolset's `-cs` choices; `numberOfFiles ≥ 1`; `runs ≥ 1`; names match `^[A-Za-z0-9-]+$` (the site-size suites are `P`, `M`, `G`, `GG`); each suite may carry a human `description`; `ranked` defaults to `true`. Bumping a suite's cells or runs requires bumping `version`. Ranking groups by name and version, so results from different versions never share a table.

### Why these cells

`standard` has 5 cells: (100, 0.500), (100, 500), (1000, 0.500), (1000, 500), (10000, 0.500). `stress` has 4 cells: (100000, 0.500), (10000, 500), (1000, 1000), (100, 5000). The cell (10000, 500) is in `stress` only (maintainer decision, 2026-10-04; spec "Decisions log").

Input sizes follow 005: 512 bytes per block; `0.500` = 1 block, `500` = 1000 blocks.

| Cell | Posts | Markdown in | What it isolates |
|---|---|---|---|
| 10 × 0.500 (smoke) | 10 | 5 KB | start-up cost and conformance; CI-sized; 1 run because it checks that things work, not how fast |
| 100 × 0.500 | 100 | 51 KB | fixed overhead (runtime boot, bundler, config load) dominates |
| 1000 × 0.500 | 1000 | 512 KB | per-file overhead starts to show |
| 10000 × 0.500 | 10000 | 5.1 MB | per-file overhead dominates: collection handling, template calls, file writes |
| 100 × 500 | 100 | 51 MB | markdown parser throughput on large documents, with few files |
| 1000 × 500 | 1000 | 512 MB | parser throughput plus memory pressure |
| 10000 × 500 (stress) | 10000 | 5.12 GB | both at once; memory limits, where `timeout` and `oom` are expected outcomes |
| 100000 × 0.500 (stress) | 100000 | 51 MB | file count scaling an order beyond `standard`; the index has 100000 items |
| 1000 × 1000 (stress) | 1000 | 1 GB | parser throughput at 1 MB posts |
| 100 × 5000 (stress) | 100 | 512 MB | very large single documents (5 MB each) |

Three decades of nf at cs = 0.500 give the scaling exponent (R-25) where per-file cost dominates. At cs = 500, where parsing dominates, `standard` has only two points (nf 100 and 1000), so it reports no exponent there (R-25 needs 3 points) and shows the two medians; the (10000, 500) point is in `stress`. Five runs is the smallest count for which a stddev is meaningful and a median robust to one outlier. `stress` uses 3 runs because each run takes minutes to hours, and its job is to find the breaking points (`timeout`, `oom`), not to rank closely matched generators.

### Site-size suites (P, M, G, GG)

Decided by the maintainer on 2026-10-05 (spec "Decisions log" 4). Each has 2 cells, 5 KB and 50 KB per page (`contentSize` `5` = 10 blocks, `50` = 100 blocks, per SF 005).

| Suite | Description | Pages | Cells | Runs | Cooldown | Timeout |
|---|---|---|---|---|---|---|
| P | website pessoal (ex.: site de professor) | 50 | (50, 5), (50, 50) | 5 | 15 s | 1 h |
| M | site corporativo | 1000 | (1000, 5), (1000, 50) | 5 | 15 s | 2 h |
| G | grande portal | 10000 | (10000, 5), (10000, 50) | 3 | 30 s | 4 h |
| GG | portal massivo | 100000 | (100000, 5), (100000, 50) | 1 | 60 s | 5 h |

Rationale for runs: small sites build in seconds, so 5 runs are cheap and give a meaningful stddev and median. G builds take minutes, so 3 runs trade precision for time. GG is a single run per cell because one build can take an hour or more on slow generators; it finds breaking points (`timeout`, `oom`) and, with `runs = 1`, has `cv = null` and no `noisy` flag. The GG timeout (5 h) stays under the 6 h GitHub-hosted job limit. In `benchmark-round.yml` the `suite` input expands to generator x cell jobs (17 x 2 = 34, under the 256 job matrix limit); the aggregate job merges per cell (`merge_results --by-cell`) and writes `suite-summary.csv/md`.

## Order

Within a cell, generators run in `rotate(sorted(names), (7 * cell_index) mod len(names))`, a left rotation. This spreads thermal and background drift across generators instead of always penalising the last one alphabetically. The rotation is deterministic, so two runs of a suite have the same order. The order is recorded in `suite.json` as `order[cell_index]`.

## Resources

- `nano_cpus = int(cpus * 1e9)`, `mem_limit = memory`, `memswap_limit = memory` (no swap), `cpuset_cpus` as computed below. The same values go to every `containers.run` of the run.
- `--cpuset auto`: with `n = docker.info()['NCPU']` and `c = ceil(cpus)`, if `n ≥ c + 1` then `cpuset_cpus = f"{n - c}-{n - 1}"` (the highest-numbered CPUs, leaving CPU 0, which handles most interrupts, to the host); otherwise `None`. `--cpuset none` gives `None`. `--cpuset 2-5` passes the value through after validating it against `n`.
- On Docker Desktop these are VM vCPUs, not physical cores. The pinning is still applied and is recorded, but its value is weaker (threat T1).
- The existing global `mem_limit = 95% of host RAM` in `docker_helper.py` is replaced by the configured `--memory` for benchmark containers.

## Peak RSS

Decision: `peakRssBytes = max(memory_usage_byte)` from hyperfine's JSON.

| Option | Measures | Problems |
|---|---|---|
| **hyperfine `memory_usage_byte`** (chosen) | `getrusage(RUSAGE_CHILDREN).ru_maxrss` × 1024 (Linux), per timed run; identical to `/usr/bin/time -v` "Maximum resident set size" | running maximum across runs; largest single process, not the sum over workers |
| `/usr/bin/time -v` around the build | same quantity, per invocation | needs the `time` package in every image and a wrapper inside the timed command (or a separate untimed build); `build.sh` changes |
| cgroup v2 `memory.peak` | sum over all processes in the container | includes page cache charged by writing output (GBs at large cells); covers content generation and verification, not only timed runs; reset needs kernel ≥ 6.12 and a writable cgroupfs; Docker Desktop VM kernels vary |

Reported as MB (10^6 bytes) in summaries. Limitation (threat T7): multi-process generators (Gatsby workers, Next.js build workers, Nikola/doit) are under-reported relative to single-process ones. This is stated in the `summary.md` caveat block.

## Marker drafts for SF 001

Task 11 adds these to SF 001 "Contracts" (marker table) and implements them in `build.sh`:

| Marker | When | Format |
|---|---|---|
| `SSGBERK_INPUT files=<n> bytes=<b>` | right after content generation | `n` = files written, `b` = sum of their sizes |
| `SSGBERK_OUTPUT files=<n> bytes=<b>` | after the verification build and conformance check, before `STARTTIME` | regular files under `output_folder`, recursive |

`build.sh` snippet (GNU findutils in `ubuntu:24.04`):

```bash
read -r in_files in_bytes < <(find "${content_folder}" -maxdepth 1 -type f -name "${dated_pattern}" -printf '%s\n' | awk '{n++; s+=$1} END {print n+0, s+0}')
echo "SSGBERK_INPUT files=${in_files} bytes=${in_bytes}"
read -r out_files out_bytes < <(find "${output_folder}" -type f -printf '%s\n' | awk '{n++; s+=$1} END {print n+0, s+0}')
echo "SSGBERK_OUTPUT files=${out_files} bytes=${out_bytes}"
```

## Results schema additions

Top level (example values):

```json
{
  "schemaVersion": 2,
  "suite": {"name": "standard", "version": 1, "cellIndex": 3, "cellCount": 5, "runs": 5, "ranked": true},
  "profile": "core",
  "resources": {"cpus": 4.0, "memoryBytes": 8589934592, "swap": false, "cpuset": "4-7"},
  "protocol": {"coldRebuild": true, "warmupBuilds": 1, "sequential": true, "concurrent": false,
               "cooldownSeconds": 15, "timeoutSeconds": 7200, "cvThreshold": 0.10},
  "environment": {
    "fingerprint": "3f9c1a7b20de",
    "cpuModel": "Apple M3 Pro", "cpuModelSource": "launcher",
    "host": {"os": "Darwin 27.0.0 arm64"},
    "docker": {"serverVersion": "29.0.1", "apiVersion": "1.52", "operatingSystem": "Docker Desktop",
               "osType": "linux", "kernelVersion": "6.12.5-linuxkit", "architecture": "aarch64",
               "ncpu": 8, "memTotalBytes": 16764911616, "cgroupVersion": "2", "storageDriver": "overlayfs"},
    "toolset": {"commit": "d6ea28c", "python": "3.12.3", "dockerPy": "7.1.0"}
  },
  "generators": {
    "hugo": {"version": "0.167.0", "versionSource": "generators.json",
             "imageId": "sha256:…", "baseImage": "ubuntu:24.04", "baseImageDigest": "ubuntu@sha256:…"}
  },
  "imageBuild": {"hugo": {"seconds": 41.8, "imageId": "sha256:…", "sizeBytes": 412000000, "noCache": false}},
  "unsupported": {"datarate": []},
  "failureReasons": {"gatsby": "oom"}
}
```

Per result (`rawData.datarate.<fw>[0]`), added keys:

```json
{
  "user": 3.91, "system": 0.62, "cpuUtilization": 1.73,
  "memoryUsageBytes": [512000000, 514000000], "peakRssBytes": 514000000,
  "inputFiles": 1000, "inputBytes": 512000000, "outputFiles": 1004, "outputBytes": 905000000,
  "cv": 0.021, "noisy": false,
  "postsPerSecond": 381.7, "inputMBPerSecond": 195.4,
  "status": "ok", "features": [],
  "attempts": [{"minRuns": 5, "mean": 2.61, "median": 2.62, "stddev": 0.055, "cv": 0.021}]
}
```

`status` ∈ `ok`, `failed`, `nonconformant`, `timeout`, `oom`, `unsupported`. Existing keys (`mean`, `stddev`, `median`, `min`, `max`, `times`, `numberOfFiles`, `contentSize`, `minRuns`, `startTime`, `endTime`) are unchanged.

`environment.fingerprint` = first 12 hex characters of `sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")))`, where `obj` = `{cpuModel, docker.ncpu, docker.memTotalBytes, docker.kernelVersion, docker.operatingSystem, docker.architecture, docker.serverVersion, resources.cpus, resources.memoryBytes, resources.cpuset}`. Timestamps, git commits and generator versions are excluded, so the fingerprint names a machine plus a resource configuration.

## `suite.json`

```json
{
  "schemaVersion": 1, "suite": "standard", "version": 1, "profile": "core",
  "startTime": 1791100000000, "completionTime": 1791190000000,
  "fingerprint": "3f9c1a7b20de",
  "cells": [{"index": 0, "numberOfFiles": 100, "contentSize": "0.500", "dir": "core/nf100-cs0.500",
             "order": ["astro", "eleventy", "…"], "succeeded": 17, "failed": 0, "unsupported": 0}]
}
```

## Statistics

- `cv = stddev / mean`. It is `null` when `runs = 1` or `stddev` is `null`.
- Ranking (R-24), per group: sort by `median`. Walk in order: generator k+1 shares generator k's rank if `min[k+1] ≤ max[k]`, otherwise it takes rank = position. Shared ranks print as `=n`.
- Scaling exponent (R-25): points `(log10 nf, log10 median)` over the suite's cells with equal `contentSize`. With `p ≥ 3` points, `b = Σ(x−x̄)(y−ȳ) / Σ(x−x̄)²`, printed with 2 decimals. `b ≈ 1` means linear, `b < 1` means fixed overhead dominates, and `b > 1` means superlinear.
- Throughput uses the median, so it is consistent with the headline.

## `summary.md` additions (per cell)

1. Header lines: `Suite: standard v1 · cell 4/5 (nf 1000, cs 500) · profile core · fingerprint 3f9c1a7b20de · resources 4 CPU / 8.0 GB / cpuset 4-7`.
2. Table columns: `Rank`, `Framework`, `Median (s)`, `CV`, `Min–Max (s)`, `Posts/s`, `MB/s`, `CPU (cores)`, `Peak RSS (MB)`, `Output (MB / files)`, `Image build (s)`. `noisy` rows get the suffix ` ⚠`.
3. "Failed / timeout / oom / nonconformant / unsupported" list with `failureReasons`.
4. Caveat block when applicable (R-30), with fixed texts per threat id (T1, T5, T7, T9).

## Validity threats

| Id | Threat | Effect | Mitigation | Reported |
|---|---|---|---|---|
| T1 | Docker Desktop on macOS/Windows: Linux VM, vCPUs time-shared with the host, virtualised disk | absolute times not comparable with native Linux; more noise | fingerprint separates environments; caveat block; reference rounds on native Linux | `environment.docker.operatingSystem`, caveat |
| T2 | Thermal throttling / turbo on laptops | later and longer runs slow down | rotated order; cool-down; CV re-run; `noisy` flag | `cv`, `noisy` |
| T3 | Filesystem caches | the first run after image build reads from disk | untimed verification build warms the page cache for all timed runs; same for every generator | protocol text |
| T4 | Overlay filesystem write cost | output written to the container's writable layer; large outputs pay overlayfs cost | identical for all generators; `storageDriver` recorded | `environment.docker.storageDriver` |
| T5 | Bundler-dominated JS generators at small N (Gatsby, Next.js, Astro, VitePress) | at 100 × 0.500 the ranking measures bundler start-up, not content handling | report the full matrix and the scaling exponent; never quote a single small cell as "the" result | caveat at nf ≤ 100 |
| T6 | Core vs Extended comparability | Extended feature sets differ per generator | separate series; ranking only within identical feature sets | `profile`, `features` |
| T7 | Peak RSS is the largest process, not the sum | under-reports multi-process generators | stated limitation; raw list stored | caveat |
| T8 | Background load / concurrent benchmarks | inflated times | concurrency guard (R-18); `--cpuset auto` away from CPU 0 | `protocol.concurrent` |
| T9 | Memory limit kills generators that keep all content in memory | `oom` instead of a time | reported as an outcome; same limit for all | `status: oom` |
| T10 | Image and dependency drift | versions change between rounds | image ids, base digest and generator versions recorded | `generators.*` |
| T11 | Unavoidable generator-specific work (for example VitePress Shiki, SF 005 open question 5) | extra work counted for that generator | documented in the generator README; part of the generator's real cost | README link in caveat |

## Decisions

| Decision | Chosen | Alternatives considered |
|---|---|---|
| Suite format | JSON data file | bash scripts like `benchmark_test.sh` (not testable, no versioning) |
| Suite output | one standard `results.json` per cell + `suite.json` index | one big `results.json` with cells (breaks BT 002/006 readers and `--parse`) |
| Headline | median | mean (sensitive to one slow run); min (optimistic; hides GC and JIT variance) |
| Dispersion | CV + min–max | stddev alone (not comparable across scales); IQR (meaningless at 5 runs) |
| Noise rule | one re-run with doubled runs; keep the last attempt | keep the best attempt (cherry-picking); unlimited re-runs (never terminates on a noisy host) |
| Peak RSS | hyperfine `memory_usage_byte` | `/usr/bin/time -v`, cgroup `memory.peak` (see "Peak RSS") |
| Resources | fixed `--cpus`/`--memory`, swap off, `--cpuset auto` | host defaults (not comparable); per-generator tuning (unfair) |
| Concurrency | refuse unless `--allow-concurrent` | silently allow (BT 004 makes it safe but not fair) |
| Order | deterministic rotation per cell | alphabetical (systematic drift bias); random (non-reproducible) |
| Warm-up | the verification build | hyperfine `--warmup 1` (an extra full build per cell; duplicates the verification build) |

## Risks

1. **Suite duration.** `standard` at 17 generators may take several hours on a laptop, dominated by 1000 × 500 and 10000 × 0.500. The 5.12 GB cell (10000 × 500) is in `stress`, where `timeout` (14400 s) and `oom` under the 8 GB limit are expected outcomes, and `stress` may take a day. Mitigation: `timeoutSeconds`, per-cell result directories (a crash loses one cell, and `--parse` re-parses it), and `--test`/`--exclude` work with `--suite`.
2. **Container removal hides OOM.** `remove=True` deletes the container before its state can be inspected. Task 4 switches to `wait()` → `inspect` → `remove`.
3. **Docker API field drift.** `info()` keys differ slightly across Docker versions. Every field is read with `.get()`, and a missing field is `null`.
4. **BT 004/006 not merged.** Tasks 5 and 10 cannot start before them. Tasks 1–4, 6–9 and 11 are independent.

## Cross-references

- Markers and `build.sh` behaviour: SF `docs/specs/001-canonical-build-runner/plan.md` (Contracts).
- Reference site and profiles: SF `docs/specs/005-reference-site-design/plan.md`.
- Conformance markers and `profile` env: SF `docs/specs/006-layout-conformance/plan.md` ("Contract drafts for 001").
- Base parser: BT `docs/specs/002-hyperfine-results`. Run ids/labels: BT `docs/specs/004-concurrent-safe-runs`. Summary files: BT `docs/specs/006-results-summary`.
- Generator versions: SF `generators.json` (SF `docs/specs/004-generator-metadata`, `docs/metadata/README.md`).
