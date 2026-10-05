# Benchmark Round 2026 — Plan

Spec: `spec.md`. Tasks: `tasks.md`. Runs last, after every other spec.

## Architecture

No new code: bump the `frameworks` submodule pointer to the modernized `ssg-frameworks` branch, run the full round, commit the example results, and add the end-to-end smoke job to BT CI.

## Decisions

- The submodule pointer is recorded locally until the human pushes the `ssg-frameworks` branch (see Task 1, Step 3 in `tasks.md`).
- Worktree cleanup happens only after the human decides how to integrate (see Task 1 end note).

## Risks

- **Ruído no Docker Desktop (macOS):** números locais servem para validar, não para publicar; resultados oficiais vêm de Linux nativo.

## Delivery order (design 7)

6. **benchmark-tool:** bump do submodule + rodada completa + `docs/results/example-2026-10.json`.

Ao final: `git worktree remove` + `git worktree prune` nos dois repos. Os ~85 branches abertos do dependabot ficam obsoletos; fechá-los só com aprovação explícita.

## Deviations

Controller rulings (2026-10-04), binding:

- **CI execution.** The full round runs on GitHub Actions (maintainer approved; the host disk is too tight for a local run) as a per-generator matrix plus an aggregate job (`.github/workflows/benchmark-round.yml`), because one sequential job exceeds the 6 h runner limit. Cost: generators are measured on different runner instances; see `docs/results/README.md`. Rigorous ranking is BT spec 008.
- **Example parameters.** The example round uses `-nf 100 -cs 0.500 -mr 3` instead of `-cs 500`: gatsby at `-cs 500` took 719 s per 10 posts (about 8 h for 100 posts x 4 builds), over the runner limit. `-cs 500` was already validated for all 17 generators by CI smoke runs 37240353439 and 37241438300 and local runs. Cost: the example does not show large-post scaling.
- **New code.** `toolset/utils/merge_results.py` (with tests) merges per-generator results; this supersedes "No new code" in the plan.
- The local full-run steps (Task 1 Steps 1-2) are replaced by the workflow; the example file is committed after the run.
