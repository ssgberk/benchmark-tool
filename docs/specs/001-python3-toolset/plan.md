# Python 3 Toolset — Plan

Spec: `spec.md`. Tasks: `tasks.md`.

## Architecture (design 3)

**Port mínimo para Python 3**, mantendo a estrutura herdada do TFB (`toolset/benchmark`, `toolset/utils`, `BenchmarkConfig`, `Benchmarker`, `DockerHelper`, `Results`, `Metadata`, scaffolding, audit, continuous, vagrant).

Alternativas descartadas:

- **Re-fork do upstream TFB atual:** o toolset atual do TFB é ainda mais voltado a servidores HTTP (wrk, bancos de dados, verificação de URLs). Seria preciso remover a maior parte, sem benefício real em ficar próximo do upstream.
- **Reescrita enxuta:** reduziria o código e o legado, mas é uma mudança maior do que a desejada agora.

Única exceção ao "port mínimo": a correção do parse de resultados (seção 4.3), sem a qual o benchmark não produz resultados.

## Contracts

- Toolset image tag: `ssgberk/toolset`. Generator image tag: `ssgberk/test.<name>`. No `matheusrv` strings may remain in `toolset/`, `ssgberk`, or `Dockerfile`.
- `-cs` values and meaning (KB per post): `0.500`=1 paragraph, `500`=1000, `1000`=2000, `5000`=10000, `10000`=20000, `100000`=200000 paragraphs. Default `0.500`.

Function-level interfaces (`build_parser()`, `DockerHelper.is_ssgberk_test_image()`, `changed_tests()`, the `fake_benchmarker` fixture) are listed under **Interfaces** in each task of `tasks.md`.

## Decisions

- Minimal port over re-fork or rewrite (see Architecture).
- `docker_helper.benchmark` keeps `"/bin/bash ./build.sh"` without `&` (see spec, Port Python 2 → 3).
- Image filters use the `ssgberk/` prefix and exclude `ssgberk/toolset` (see spec, Toolset image).

## Risks and measurement notes

- **Bundlers dominam o tempo de geradores JS "app-like" (Gatsby, Next.js, Astro, VitePress) com poucos arquivos.** É o comportamento real deles; fica documentado no README, sem ajuste.
- **Ruído no Docker Desktop (macOS):** números locais servem para validar, não para publicar; resultados oficiais vêm de Linux nativo.
- **Cenários grandes (`-nf 1000000`) em `build.sh` bash:** a geração de conteúdo via loop + `sponge` é lenta. Mantida no port mínimo; registrada como melhoria futura.

## Delivery order (design 7)

Cada passo é um PR independente com CI verde. Trabalho no branch `chore/modernize-2026` de cada repo, em worktrees isolados; commits assinados (GPG `B6FA8458D5176E83`).

1. **benchmark-tool:** Dockerfile do toolset + port Py3 + renomeação de imagens + unitários.
