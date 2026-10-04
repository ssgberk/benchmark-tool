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
