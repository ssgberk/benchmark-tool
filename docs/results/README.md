# Benchmark rounds

## Running a round

Rounds run on GitHub Actions through the `benchmark-round` workflow
(`.github/workflows/benchmark-round.yml`, manual dispatch):

```bash
gh workflow run benchmark-round.yml \
  -f number_of_files=100 -f content_size=0.500 -f min_runs=3
# optional: -f tests="hugo zola"   (empty = all generators)
gh run list --workflow benchmark-round.yml
gh run download <run-id> -n benchmark-round
```

The workflow lists the generators from `frameworks/*/*/benchmark_config.json`,
runs one matrix job per generator (`./ssgberk --test <name> ...`, up to 300
minutes each) and then merges everything.

## Artifacts

- `result-<test>`: one per generator; the `results/<timestamp>/` directory
  (`results.json`, raw output, `test_metadata.json`) plus `env-<test>.txt`
  (`lscpu`, `nproc`, `free -m`, Docker version, `uname -a`).
- `benchmark-round`: the merged round: `results.json` (same schema as a
  normal run plus an `environments` map), `summary.csv`, `summary.md`, and
  `runs/` with every per-generator artifact. Produced by
  `python3 -m toolset.utils.merge_results`.

## Validity caveat

Each generator is measured on a different, shared GitHub-hosted runner, so
hardware and neighbour noise differ between generators. Rankings are
indicative only. Rigorous methodology (dedicated hardware, repeated rounds,
confidence intervals) is spec 008.

## Example results

`docs/results/example-2026-10.json` will be committed by the controller after
the first round has run (`-nf 100 -cs 0.500 -mr 3`).

## Example round (2026-10)

- Workflow run: https://github.com/ssgberk/benchmark-tool/actions/runs/37249532656 (commit `79f0254`, ssg-frameworks `ff2a6a3`).
- Parameters: `number_of_files=100`, `content_size=0.500`, `min_runs=3`; 17/17 generators succeeded.
- Files: [`example-2026-10.json`](example-2026-10.json) (merged results), [`example-2026-10.csv`](example-2026-10.csv) and [`example-2026-10.md`](example-2026-10.md) (summary).
- Indicative only: each generator ran on a different shared GitHub runner. Rankings for publication follow `docs/specs/008-benchmark-methodology` (fixed resources, one machine, noise control).
