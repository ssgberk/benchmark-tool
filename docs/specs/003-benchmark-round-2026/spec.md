# Benchmark Round 2026

- **Repo:** `ssgberk/benchmark-tool`
- **Date:** 2026-10-04
- **Status:** proposed, awaiting review (approved design redistributed from `2026-10-04-modernize-ssgberk-design.md`)
- **Siblings:** `plan.md` (how), `tasks.md` (executable task list) in this directory; roadmap in `benchmark-tool/docs/specs/ROADMAP.md`

## Context

| Item | Hoje | Problema |
|---|---|---|
| Submodule | `frameworks` → `fea944a` | Anterior ao commit "Round 1 Working Version" do `ssg-frameworks` |

- `.gitmodules`: continua `ssgberk/ssg-frameworks`, `branch = master`. O ponteiro é atualizado no último passo (seção 7).

## Requirements

O trabalho está pronto quando:

2. Uma rodada `./ssgberk -nf 100 -cs 500 -mr 3` com todos os geradores gera um `results.json` com os 17 em `succeeded.datarate`, cada um com `mean > 0`. Esse arquivo vai commitado em `docs/results/example-2026-10.json`.
3. O CI está verde nos dois repos.

- `benchmark-tool`: `compileall`, `ruff`, `pytest`; em PR, smoke test de `hugo` (prova toolset + submodule).

## Acceptance criteria

2. Uma rodada `./ssgberk -nf 100 -cs 500 -mr 3` com todos os geradores gera um `results.json` com os 17 em `succeeded.datarate`, cada um com `mean > 0`. Esse arquivo vai commitado em `docs/results/example-2026-10.json`.
3. O CI está verde nos dois repos.

## Out of scope

- Site de resultados (`ssgberk.matheusrv.com`).
- O monorepo `StaticSiteGeneratorBenchmark`.

## Deviations

Controller rulings (2026-10-04), binding:

- **CI execution.** The full round runs on GitHub Actions (maintainer approved; the host disk is too tight for a local run) as a per-generator matrix plus an aggregate job (`.github/workflows/benchmark-round.yml`), because one sequential job exceeds the 6 h runner limit. Cost: generators are measured on different runner instances; see `docs/results/README.md`. Rigorous ranking is BT spec 008.
- **Example parameters.** The example round uses `-nf 100 -cs 0.500 -mr 3` instead of `-cs 500`: gatsby at `-cs 500` took 719 s per 10 posts (about 8 h for 100 posts x 4 builds), over the runner limit. `-cs 500` was already validated for all 17 generators by CI smoke runs 37240353439 and 37241438300 and local runs. Cost: the example does not show large-post scaling.
- **New code.** `toolset/utils/merge_results.py` (with tests) merges per-generator results; this supersedes "No new code" in the plan.
- The local full-run steps (Task 1 Steps 1-2) are replaced by the workflow; the example file is committed after the run.
