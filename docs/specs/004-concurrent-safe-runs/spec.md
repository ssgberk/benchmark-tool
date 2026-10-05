# 004 Concurrent-safe runs

## Problem
Two `./ssgberk` processes on one Docker host interfere:
- `run()` names the container `ssgberk-server` when a network is set, so a second run hits a name conflict.
- `stop()` with no args stops every container whose image tag starts with `ssgberk/test.`, killing the other run's containers.
- `__stop_all` reads `container.image.tags`, which raises `docker.errors.ImageNotFound` if the image was removed or re-tagged meanwhile (seen in a real run).
- `BenchmarkConfig.timestamp` (`%Y%m%d%H%M%S`) names `results/<ts>/`; two runs started in the same second share it.

## Requirements
1. Each run has a `run_id` (uuid4 string) created in `BenchmarkConfig`; `Results.uuid` reuses it.
2. Every container created by `run()` and `benchmark()` carries the label `ssgberk.run=<run_id>`.
3. `stop()` with no arguments stops only containers labelled with this run's id (filter `label=ssgberk.run=<id>`), not image-tag based.
4. Container names are unique per run: `ssgberk-<run_id[:8]>-<test>`.
5. `docker.errors.NotFound` and `ImageNotFound` are tolerated when listing/stopping.
6. If `results/<timestamp>` already exists (new run, not `--parse`), the timestamp gets a suffix `-2`, `-3`, ... and the directory is claimed atomically (`os.makedirs` without `exist_ok`). `--parse <ts>` keeps using `<ts>` verbatim.
7. `clean()` still removes all `ssgberk/test.*` images (intended global cleanup).

## Decision: container name
Nothing in the repo resolves the name `ssgberk-server` (grep of `server_host`, `extra_hosts`, `ssgberk-server`): the `--server-host` default only feeds `extra_hosts` when `network is None` (that branch is unchanged) and the tcp docker host in host mode. There is no web server under test any more; the container just runs `build.sh`. So the DNS name on the `ssgberk` network is unused and a fixed name only causes conflicts. A unique, readable name per run and test is kept for `docker ps` usability.

## Acceptance
- Unit tests with a mocked docker client cover labels, name, scoped stop, not-found tolerance, results dir suffix, `--parse`.
- E2E: two concurrent `./ssgberk --test hugo -nf 10 -mr 1` runs both succeed with distinct results dirs.

## Out of scope
Locking of the shared `ssgberk/test.<name>` image tag (concurrent builds of the same test still share the tag); network creation races.
