# SSGBerk Modernization — Roadmap

- **Date:** 2026-10-04
- **Repos:** `ssgberk/benchmark-tool` (BT, toolset) and `ssgberk/ssg-frameworks` (SF, submodule `frameworks/`)

## Goal

Rodar `./ssgberk` numa máquina atual (Docker 29, Linux amd64 ou macOS arm64) e obter tempos de build reproduzíveis para um conjunto atual de SSGs, gravados no `results.json`.

## Child specs

Each spec has `spec.md`, `plan.md`, `tasks.md` in its directory.

| Spec | Repo | Purpose |
|---|---|---|
| `docs/specs/001-python3-toolset` | BT | Python 3 toolset image, port, CLI fixes, GitHub Actions, Vagrant, README |
| `docs/specs/002-hyperfine-results` | BT | Parse the hyperfine JSON from `build.sh` markers into `results.json`; `dool` stats |
| `docs/specs/003-benchmark-round-2026` | BT | Submodule bump, full benchmark round, example results, CI smoke job |
| `docs/specs/008-benchmark-methodology` | BT | Suites (smoke/standard/stress), Core/Extended series, resource limits, sequential protocol, CPU/RSS/IO metrics, noise control, environment capture, rankings |
| `docs/specs/001-canonical-build-runner` | SF | Canonical `build.sh`, `benchmark_config.json` schema and marker contract, Dockerfile skeleton, Hugo, CI |
| `docs/specs/002-update-existing-generators` | SF | Update 8 existing generators, remove 5 dead ones |
| `docs/specs/003-new-generators` | SF | Add 8 new generators |

## Execution order and dependencies

1. BT 001-python3-toolset (no dependencies).
2. BT 002-hyperfine-results (needs BT 001; consumes the marker contract owned by SF 001-canonical-build-runner).
3. SF 001-canonical-build-runner, Task 1 (build.sh + Hugo; end-to-end validation needs BT 001 and BT 002).
4. SF 002-update-existing-generators (needs SF 001 Task 1).
5. SF 003-new-generators (needs SF 001 Task 1).
6. SF 001-canonical-build-runner, Task 2 (CI; needs SF 002 and SF 003 so every `build.sh` is canonical).
7. BT 003-benchmark-round-2026 (needs everything above).

Each step is an independent PR with green CI, on branch `chore/modernize-2026` of each repo, in isolated worktrees.

## Workspace layout

## Workspace layout (already created / created in `001-python3-toolset` Task 1)

```
/Users/jobs/Dev/ssgberk/
  benchmark-tool/                         # main checkout, branch master — DO NOT EDIT
  ssg-frameworks/                         # main checkout, branch master — DO NOT EDIT
  StaticSiteGeneratorBenchmark/           # monorepo, read-only reference source
  .worktrees/benchmark-tool-modernize/    # benchmark-tool, branch chore/modernize-2026  ← BT
  .worktrees/benchmark-tool-modernize/frameworks/
                                          # ssg-frameworks worktree, branch chore/modernize-2026 ← SF
```

In these specs **BT** = `/Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize` and **SF** = `BT/frameworks`. SF lives inside BT on purpose: `./ssgberk` mounts BT into the toolset container and reads generators from `BT/frameworks`, so local end-to-end runs exercise the in-progress generators without touching the submodule pointer.

## Git rules

- Git author/committer `Matheus Breguêz <matbrgz@gmail.com>`; every commit GPG-signed (repo config already has `commit.gpgsign=true`, key `B6FA8458D5176E83`). Never use `--no-gpg-sign` or `--author`.
- Every commit message ends with the trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Never commit to `master`. Never push, open PRs, or close dependabot branches unless the human explicitly asks.

Ao final: `git worktree remove` + `git worktree prune` nos dois repos. Os ~85 branches abertos do dependabot ficam obsoletos; fechá-los só com aprovação explícita.
