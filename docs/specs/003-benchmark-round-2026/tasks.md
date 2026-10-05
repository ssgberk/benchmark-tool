# Benchmark Round 2026 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Point `frameworks/` at the modernized generators, run the full benchmark (`-nf 100 -cs 500 -mr 3`), commit the example `results.json`, and add the end-to-end smoke job to BT CI.

**Architecture:** No new code: a submodule pointer bump, one full `./ssgberk` run, `docs/results/example-2026-10.json`, and a `smoke` job appended to `.github/workflows/ci.yml`.

**Tech Stack:** Docker 29, `./ssgberk`, jq, GitHub Actions.

**Spec:** `docs/specs/003-benchmark-round-2026/spec.md` and `docs/specs/003-benchmark-round-2026/plan.md` (same directory, repo `ssgberk/benchmark-tool`). Read both before starting any task.

In this file **BT** = `/Users/jobs/Dev/ssgberk/.worktrees/benchmark-tool-modernize` (repo `ssgberk/benchmark-tool`, branch `chore/modernize-2026`) and **SF** = `BT/frameworks` (repo `ssgberk/ssg-frameworks`, branch `chore/modernize-2026`). Layout: `docs/specs/ROADMAP.md` in BT.

Prerequisites: `docs/specs/001-python3-toolset` and `docs/specs/002-hyperfine-results` in BT, and `ssg-frameworks` specs `001-canonical-build-runner`, `002-update-existing-generators`, `003-new-generators` are complete.

## Global Constraints

- Git author/committer `Matheus Breguêz <matbrgz@gmail.com>`; every commit GPG-signed (repo config already has `commit.gpgsign=true`, key `B6FA8458D5176E83`). Never use `--no-gpg-sign` or `--author`.
- Every commit message ends with the trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- Never commit to `master`. Never push, open PRs, or close dependabot branches unless the human explicitly asks.

---

### Task 1: Submodule bump, full run, example results, smoke job (BT)

- [ ] **Step 1: Full local run** (BT):

```bash
./ssgberk --clean
./ssgberk -nf 100 -cs 500 -mr 3
R=$(ls -td results/*/ | head -1)
jq '.succeeded.datarate | length' "$R/results.json"    # Expected: 17 (minus any _wip fallbacks)
jq '.failed.datarate' "$R/results.json"                # Expected: []
jq -r '.rawData.datarate | to_entries[] | "\(.key)\t\(.value[0].mean)"' "$R/results.json" | sort -k2 -n
```

- [ ] **Step 2:** `mkdir -p docs/results && cp "$R/results.json" docs/results/example-2026-10.json`. Add a short `docs/results/README.md`: date, machine (`uname -m`, Docker version, CPU), command used, note that macOS numbers are for validation only.

- [ ] **Step 3: Submodule pointer** — the SF branch must exist on the remote before the pointer is useful to others; until the human pushes, record the commit locally:

```bash
SF_HEAD=$(git -C frameworks rev-parse HEAD)
git add frameworks
git ls-files -s frameworks    # Expected: 160000 <SF_HEAD> 0	frameworks
```

- [ ] **Step 4: Smoke job** — append to BT `.github/workflows/ci.yml`:

```yaml
  smoke:
    needs: toolset
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
      - run: ./ssgberk --test hugo -nf 10 -cs 0.500 -mr 1
      - run: |
          R=$(ls -td results/*/ | head -1)
          jq -e '.rawData.datarate.hugo[0].mean > 0' "$R/results.json"
```

- [ ] **Step 5: Commit (BT)** — `git add docs/results .github/workflows/ci.yml && git commit -m "chore: bump ssg-frameworks to modernized generators; add example results" -m "Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"`

- [ ] **Step 6: Final verification (BT)** — `.venv/bin/pytest -q && .venv/bin/ruff check toolset tests && (cd frameworks && tools/check-build-sh.sh)`; all pass.

Worktree cleanup (`git worktree remove` + `git worktree prune` in both repos) happens only after the human decides how to integrate (push/PR/merge) — not in this task.

## Deviations

Controller rulings (2026-10-04), binding:

- **CI execution.** The full round runs on GitHub Actions (maintainer approved; the host disk is too tight for a local run) as a per-generator matrix plus an aggregate job (`.github/workflows/benchmark-round.yml`), because one sequential job exceeds the 6 h runner limit. Cost: generators are measured on different runner instances; see `docs/results/README.md`. Rigorous ranking is BT spec 008.
- **Example parameters.** The example round uses `-nf 100 -cs 0.500 -mr 3` instead of `-cs 500`: gatsby at `-cs 500` took 719 s per 10 posts (about 8 h for 100 posts x 4 builds), over the runner limit. `-cs 500` was already validated for all 17 generators by CI smoke runs 37240353439 and 37241438300 and local runs. Cost: the example does not show large-post scaling.
- **New code.** `toolset/utils/merge_results.py` (with tests) merges per-generator results; this supersedes "No new code" in the plan.
- The local full-run steps (Task 1 Steps 1-2) are replaced by the workflow; the example file is committed after the run.
