# Hyperfine Results (toolset side)

- **Repo:** `ssgberk/benchmark-tool`
- **Date:** 2026-10-04
- **Status:** proposed, awaiting review (approved design redistributed from `2026-10-04-modernize-ssgberk-design.md`)
- **Siblings:** `plan.md` (how), `tasks.md` (executable task list) in this directory; roadmap in `benchmark-tool/docs/specs/ROADMAP.md`

## Context

| Item | Hoje | Problema |
|---|---|---|
| Resultados | `Results.parse_test` procura saída do `wrk` | **O tempo de build medido não chega ao `results.json`**; o benchmark não produz resultado utilizável |

## Requirements

### Results parsing (design 4.3, toolset side)

The marker contract (what `build.sh` prints) is owned by `ssg-frameworks/docs/specs/001-canonical-build-runner` (its `plan.md`, Contracts). The toolset side:

- `Results.parse_test(framework_test, test_type)` passa a:
  1. ler `raw.txt` e extrair o texto entre os marcadores;
  2. `json.loads` e pegar `results[0]`;
  3. retornar `{'results': [{'mean', 'stddev', 'median', 'min', 'max', 'times', 'numberOfFiles', 'contentSize', 'minRuns'}]}`;
  4. se os marcadores não existirem, o JSON for inválido, ou a saída contiver `SSGBERK_VERIFY_FAIL` (seção 5.4), retornar `{'results': []}`. Com isso `report_benchmark_results` coloca o gerador em `failed.datarate`, sem exceção.
- O parser de `wrk` (Latency, requests, Socket errors, Non-2xx) é removido de `parse_test`.
- Parse de estatísticas do `dool` (`__parse_stats`) continua igual, chamado com `startTime`/`endTime` vindos de linhas `STARTTIME <epoch>` / `ENDTIME <epoch>` que o `build.sh` imprime antes e depois do hyperfine.

### DockerHelper raw output (design 6.1)

- `DockerHelper.benchmark` grava a saída do container no `raw.txt` byte a byte (sem `log()`), porque os chunks de `logs(stream=True)` não respeitam limites de linha e o `log()` insere quebras que corromperiam o JSON.

## Acceptance criteria

(design 6.1, results part)

- `Results.parse_test`:
  - `raw.txt` com marcadores e JSON válido → 1 resultado com `mean`, `stddev`, `min`, `max`, `times`.
  - Sem marcadores → `[]`.
  - JSON inválido entre marcadores → `[]`.
  - Contém `SSGBERK_VERIFY_FAIL` → `[]`.
- `Results.__parse_stats` com um CSV real do `dool` gravado como fixture.

## Out of scope

- Site de resultados (`ssgberk.matheusrv.com`).
- O monorepo `StaticSiteGeneratorBenchmark`.
- Changing what `build.sh` prints (owned by `ssg-frameworks/docs/specs/001-canonical-build-runner`).
