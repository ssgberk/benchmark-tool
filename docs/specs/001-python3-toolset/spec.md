# Python 3 Toolset

- **Repo:** `ssgberk/benchmark-tool`
- **Date:** 2026-10-04
- **Status:** proposed, awaiting review (approved design redistributed from `2026-10-04-modernize-ssgberk-design.md`)
- **Siblings:** `plan.md` (how), `tasks.md` (executable task list) in this directory; roadmap in `benchmark-tool/docs/specs/ROADMAP.md`

## Context

O SSGBerk é um hard fork do [TechEmpower/FrameworkBenchmarks](https://github.com/TechEmpower/FrameworkBenchmarks) que mede o **tempo de build** de static site generators (SSGs): gera N posts markdown de tamanho X, roda o build de cada gerador em um container isolado e mede com `hyperfine`.

Os dois repos estão parados desde setembro de 2019:

| Item | Hoje | Problema |
|---|---|---|
| Toolset | Python 2.7, `buildpack-deps:bionic`, docker-py 4.0.2 | Python 2 é EOL; a imagem não constrói mais |
| Métricas de recurso | `dstat` | Abandonado; substituído por `dool` no upstream |
| CI | Travis (`.travis.yml` herdado do TFB, lista frameworks web) | Travis.org desligado |

## Requirements

### Toolset image (design 4.1)

`Dockerfile`:

- Base `buildpack-deps:bionic` → `ubuntu:24.04`.
- Pacotes apt: `git-core cloc curl python3 python3-colorama python3-psutil python3-requests python3-pip`.
- `pip3 install --break-system-packages docker==7.1.0` (mesmo padrão do upstream TFB).
- `dool` v1.3.8 instalado a partir do tarball do GitHub (`./install.py`), no lugar de `dstat`. O `Benchmarker.__begin_logging` passa a chamar `dool` com as mesmas flags que existirem no dool; flags removidas no dool são retiradas.
- Remove o hack `cp -r .../backports/ssl_match_hostname`.
- `ENTRYPOINT ["python3", "/FrameworkBenchmarks/toolset/run-tests.py"]`.

Nome da imagem: `matheusrv/ssgberk` → `ssgberk/toolset`. Imagens de teste: `matheusrv/ssgberk.test.<nome>` → `ssgberk/test.<nome>`. Os filtros em `DockerHelper.clean` e `DockerHelper.__stop_all` (hoje `'matheusrv' in tag`) passam a usar o prefixo `ssgberk/`, excluindo `ssgberk/toolset`. O script `./ssgberk` usa o nome novo.

### Port Python 2 → 3 (design 4.2)

Mudanças mecânicas, sem reestruturar módulos:

- `docker_helper.__build`: `token[token.keys()[0]].encode('utf-8')` → `next(iter(token.values()))` (str).
- `docker_helper.watch_container` / `benchmark`: linhas de `container.logs(stream=True)` são `bytes` → `.decode('utf-8', 'replace')`.
- `results.__parse_stats`: `stats.next()` / `stats_reader.next()` → `next(...)`.
- `subprocess.check_output(...)` → `.decode()` onde o retorno é usado como texto (`__count_commits`, `__count_sloc`).
- Qualquer `print` statement, `except X, e`, `dict.keys()[i]`, `iteritems`, `basestring`, `unicode` encontrado por `python3 -m compileall` e `ruff check --select E9,F63,F7,F82,UP`.
- `docker_helper.benchmark`: manter `"/bin/bash ./build.sh"` **sem** `&` (a variante com `&` do monorepo faz o container sair antes de terminar o build).

Bugs corrigidos durante o port:

- `metadata.py`: chave `"versus"` duplicada no dict de metadata (versão do monorepo); manter a do `benchmark-tool`, que já está correta.
- `run-tests.py`: textos de `help` de `-nf`, `-cs`, `-mr` copiados de `--duration`; corrigir.
- `run-tests.py`: `-cs` tem `nargs='+'` (vira lista) e não aceita `100000`, que o `benchmark_test.sh` usa; o `build.sh` compara com `"[500]"`. Passa a ser um valor único, `choices=['0.500','500','1000','5000','10000','100000']`, default `0.500`. A unidade é KB por post: `0.500` = 1 parágrafo (~0,5 KB), `500` = 1000 parágrafos (~550 KB), e assim por diante (mesma tabela do `build.sh` atual). O `build.sh` compara com o número sem colchetes e ainda aceita `[N]` por compatibilidade.
- `-v/--verbose` hoje é `default=False` sem `action`, então qualquer valor vira string verdadeira; passa a `action='store_true'`.

### Infra and documentation (design 4.4)

- `.travis.yml` e `toolset/travis/` → `.github/workflows/ci.yml` + `toolset/github_actions/github_actions_diff.py` (port de `travis_diff.py`, decide quais geradores testar a partir do diff).
- Vagrant: `ubuntu/bionic64` → `bento/ubuntu-24.04`; provisionamento instala Docker Engine pelo repositório oficial.
- `toolset/continuous/*.sh`: adicionar `export LANG=C.UTF-8` (vindo do monorepo).
- `README.md`: URLs `MatheusRV/StaticSiteGeneratorBenchmarks` → `ssgberk/benchmark-tool`; remover badges de Travis, Docker Hub build e Scrutinizer; exemplos `--test gemini` → `--test hugo`; seção "Notas de medição" (seção 8); crédito ao TechEmpower mantido.
- `package.json` da raiz: remover dependências `file:./frameworks/...` (eram para o dependabot e apontam para geradores removidos).
- `.gitmodules`: continua `ssgberk/ssg-frameworks`, `branch = master`. O ponteiro é atualizado no último passo (seção 7).

## Acceptance criteria

(design 6.1, toolset part)

- `run-tests.py`: `-cs 100000` aceito como string única; `-cs 7` rejeitado; default `0.500`; `-v` sem valor → `True`.
- `python3 -m compileall -q toolset` sem erros.

## Out of scope

- Reescrever o toolset ou trocar a geração de conteúdo para Python.
- O monorepo `StaticSiteGeneratorBenchmark`.
- Results parsing (`docs/specs/002-hyperfine-results`), the generators (`ssg-frameworks`), and the benchmark round (`docs/specs/003-benchmark-round-2026`).
