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
