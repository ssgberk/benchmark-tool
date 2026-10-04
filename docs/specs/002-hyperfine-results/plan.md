# Hyperfine Results (toolset side) — Plan

Spec: `spec.md`. Tasks: `tasks.md`. Depends on `docs/specs/001-python3-toolset` (runs after it).

## Architecture

`build.sh` (in each generator, see `ssg-frameworks/docs/specs/001-canonical-build-runner/plan.md`) prints hyperfine JSON between markers; `DockerHelper.benchmark` writes the container stream verbatim to `raw.txt`; `Results.parse_test` extracts and validates the JSON; `__parse_stats` reads the `dool` CSV within the `STARTTIME`/`ENDTIME` window.

## Contracts

Contract owned by `ssg-frameworks/docs/specs/001-canonical-build-runner`. Marker strings consumed here:

- Result markers printed by `build.sh`, consumed by `Results.parse_test`: `SSGBERK_RESULT_BEGIN`, `SSGBERK_RESULT_END`, `SSGBERK_VERIFY_FAIL`, `STARTTIME <epoch>`, `ENDTIME <epoch>`.

Return shape of `Results.parse_test`: see spec, Requirements. Function interfaces: Interfaces block of Task 1 in `tasks.md`.

## Risks

1. **Chunked docker log stream corrupting the JSON** — `container.logs(stream=True)` yields arbitrary byte chunks; if `raw.txt` is written through `log()` (which appends a newline per chunk) a number like `12.34` can be split into `12.` / `34` and parsing silently fails, sending every generator to `failed`. Pinned by `test_benchmark_writes_raw_chunks_verbatim` in Task 1 of `tasks.md`.

## Delivery order (design 7)

2. **benchmark-tool:** contrato de resultados (4.3) + CI + Vagrant + README + `package.json`.

(CI, Vagrant, README and `package.json` from that step are delivered by `docs/specs/001-python3-toolset` Task 5.)
