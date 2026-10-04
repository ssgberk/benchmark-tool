# Modernização do SSGBerk (2026)

- **Data:** 2026-10-04
- **Status:** proposto, aguardando revisão
- **Repos afetados:** `ssgberk/benchmark-tool` (toolset), `ssgberk/ssg-frameworks` (submodule `frameworks/`)
- **Fora deste spec:** `ssgberk/StaticSiteGeneratorBenchmark` (monorepo). Ele é usado só como fonte das correções de `build.sh` e `continuous/` que nunca chegaram aos repos split.

## 1. Contexto

O SSGBerk é um hard fork do [TechEmpower/FrameworkBenchmarks](https://github.com/TechEmpower/FrameworkBenchmarks) que mede o **tempo de build** de static site generators (SSGs): gera N posts markdown de tamanho X, roda o build de cada gerador em um container isolado e mede com `hyperfine`.

Os dois repos estão parados desde setembro de 2019:

| Item | Hoje | Problema |
|---|---|---|
| Toolset | Python 2.7, `buildpack-deps:bionic`, docker-py 4.0.2 | Python 2 é EOL; a imagem não constrói mais |
| Métricas de recurso | `dstat` | Abandonado; substituído por `dool` no upstream |
| Geradores | `ubuntu:18.04`, Node 10, hugo 0.58.2, hyperfine 1.7.0 | Imagens EOL; binários só amd64; 8 dockerfiles com linha corrompida (`... \| bash - && /\|RUN curl ...`) |
| Resultados | `Results.parse_test` procura saída do `wrk` | **O tempo de build medido não chega ao `results.json`**; o benchmark não produz resultado utilizável |
| CI | Travis (`.travis.yml` herdado do TFB, lista frameworks web) | Travis.org desligado |
| Submodule | `frameworks` → `fea944a` | Anterior ao commit "Round 1 Working Version" do `ssg-frameworks` |
| Geradores mortos | Harp, Phenomic (arquivado em 2020), Cuttlebelle, webgen | Não instalam ou não têm manutenção |

## 2. Objetivo e critérios de sucesso

Rodar `./ssgberk` numa máquina atual (Docker 29, Linux amd64 ou macOS arm64) e obter tempos de build reproduzíveis para um conjunto atual de SSGs, gravados no `results.json`.

O trabalho está pronto quando:

1. Os 17 geradores da seção 5 passam no smoke test (seção 6.2) localmente em arm64 e no CI em amd64.
2. Uma rodada `./ssgberk -nf 100 -cs 500 -mr 3` com todos os geradores gera um `results.json` com os 17 em `succeeded.datarate`, cada um com `mean > 0`. Esse arquivo vai commitado em `docs/results/example-2026-10.json`.
3. O CI está verde nos dois repos.

## 3. Abordagem escolhida

**Port mínimo para Python 3**, mantendo a estrutura herdada do TFB (`toolset/benchmark`, `toolset/utils`, `BenchmarkConfig`, `Benchmarker`, `DockerHelper`, `Results`, `Metadata`, scaffolding, audit, continuous, vagrant).

Alternativas descartadas:

- **Re-fork do upstream TFB atual:** o toolset atual do TFB é ainda mais voltado a servidores HTTP (wrk, bancos de dados, verificação de URLs). Seria preciso remover a maior parte, sem benefício real em ficar próximo do upstream.
- **Reescrita enxuta:** reduziria o código e o legado, mas é uma mudança maior do que a desejada agora.

Única exceção ao "port mínimo": a correção do parse de resultados (seção 4.3), sem a qual o benchmark não produz resultados.

## 4. `benchmark-tool` (toolset)

### 4.1 Imagem do toolset

`Dockerfile`:

- Base `buildpack-deps:bionic` → `ubuntu:24.04`.
- Pacotes apt: `git-core cloc curl python3 python3-colorama python3-psutil python3-requests python3-pip`.
- `pip3 install --break-system-packages docker==7.1.0` (mesmo padrão do upstream TFB).
- `dool` v1.3.8 instalado a partir do tarball do GitHub (`./install.py`), no lugar de `dstat`. O `Benchmarker.__begin_logging` passa a chamar `dool` com as mesmas flags que existirem no dool; flags removidas no dool são retiradas.
- Remove o hack `cp -r .../backports/ssl_match_hostname`.
- `ENTRYPOINT ["python3", "/FrameworkBenchmarks/toolset/run-tests.py"]`.

Nome da imagem: `matheusrv/ssgberk` → `ssgberk/toolset`. Imagens de teste: `matheusrv/ssgberk.test.<nome>` → `ssgberk/test.<nome>`. Os filtros em `DockerHelper.clean` e `DockerHelper.__stop_all` (hoje `'matheusrv' in tag`) passam a usar o prefixo `ssgberk/`, excluindo `ssgberk/toolset`. O script `./ssgberk` usa o nome novo.

### 4.2 Port Python 2 → 3

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

### 4.3 Resultados (correção funcional)

Contrato entre `build.sh` e o toolset:

- `build.sh` roda `hyperfine ... --export-json /tmp/ssgberk-hyperfine.json` e, ao final, imprime no stdout:

  ```
  SSGBERK_RESULT_BEGIN
  <conteúdo de /tmp/ssgberk-hyperfine.json>
  SSGBERK_RESULT_END
  ```

- `Results.parse_test(framework_test, test_type)` passa a:
  1. ler `raw.txt` e extrair o texto entre os marcadores;
  2. `json.loads` e pegar `results[0]`;
  3. retornar `{'results': [{'mean', 'stddev', 'median', 'min', 'max', 'times', 'numberOfFiles', 'contentSize', 'minRuns'}]}`;
  4. se os marcadores não existirem, o JSON for inválido, ou a saída contiver `SSGBERK_VERIFY_FAIL` (seção 5.4), retornar `{'results': []}`. Com isso `report_benchmark_results` coloca o gerador em `failed.datarate`, sem exceção.
- O parser de `wrk` (Latency, requests, Socket errors, Non-2xx) é removido de `parse_test`.
- Parse de estatísticas do `dool` (`__parse_stats`) continua igual, chamado com `startTime`/`endTime` vindos de linhas `STARTTIME <epoch>` / `ENDTIME <epoch>` que o `build.sh` imprime antes e depois do hyperfine.

### 4.4 Infra e documentação

- `.travis.yml` e `toolset/travis/` → `.github/workflows/ci.yml` + `toolset/github_actions/github_actions_diff.py` (port de `travis_diff.py`, decide quais geradores testar a partir do diff).
- Vagrant: `ubuntu/bionic64` → `bento/ubuntu-24.04`; provisionamento instala Docker Engine pelo repositório oficial.
- `toolset/continuous/*.sh`: adicionar `export LANG=C.UTF-8` (vindo do monorepo).
- `README.md`: URLs `MatheusRV/StaticSiteGeneratorBenchmarks` → `ssgberk/benchmark-tool`; remover badges de Travis, Docker Hub build e Scrutinizer; exemplos `--test gemini` → `--test hugo`; seção "Notas de medição" (seção 8); crédito ao TechEmpower mantido.
- `package.json` da raiz: remover dependências `file:./frameworks/...` (eram para o dependabot e apontam para geradores removidos).
- `.gitmodules`: continua `ssgberk/ssg-frameworks`, `branch = master`. O ponteiro é atualizado no último passo (seção 7).

## 5. `ssg-frameworks` (geradores)

### 5.1 Contrato de um gerador (inalterado)

```
<Linguagem>/<nome>/
  benchmark_config.json   # tests[], content[], config[] (formato atual)
  <nome>.dockerfile
  build.sh                # cópia idêntica do build.sh canônico
  README.md
  src/                    # site mínimo
  package.json + package-lock.json | Gemfile + Gemfile.lock | requirements.txt | composer.json + composer.lock
```

### 5.2 Dockerfiles

- `FROM ubuntu:24.04`, `ARG DEBIAN_FRONTEND=noninteractive`.
- Arquitetura detectada com `dpkg --print-architecture` (`amd64` | `arm64`) dentro do `RUN`. **Não usar `TARGETARCH`:** o toolset constrói via `docker.APIClient.build` (builder legado), que no Docker 29 funciona mas deixa `TARGETARCH` vazio (verificado em 2026-10-04).
- Pacotes comuns: `build-essential git curl wget jq ca-certificates moreutils tree`.
- hyperfine 1.20.0: `.deb` `hyperfine_1.20.0_${ARCH}.deb`.
- Runtimes:
  - Node 24 LTS via tarball oficial `node-v24.x-linux-${arch}` (`arch` = `x64` | `arm64`); `npm ci`.
  - Ruby do apt (3.2) + `bundler`; `bundle install` com `Gemfile.lock`.
  - Python 3.12 do apt + `python3 -m venv /opt/venv`; `PATH=/opt/venv/bin:$PATH`; `pip install -r requirements.txt`.
  - PHP 8.4 via `ppa:ondrej/php` + Composer.
  - Go/Rust: binário oficial do gerador (`hugo_extended_<v>_linux-${ARCH}.deb`, `zola-v<v>-<arch>-unknown-linux-gnu.tar.gz`).
- Versão de cada gerador em `ARG <NOME>_VERSION` no topo do dockerfile; para npm/gem/pip/composer, a versão exata também fica no manifesto + lockfile.
- Remover `node_modules/` versionado em `JavaScript/gatsby` (558 arquivos).
- `Go/hugo/src/config.toml` tem `disableKinds = ["page", ...]`: o Hugo nunca gerou HTML de posts. Remover `"page"` dessa lista; a verificação de saída (5.4) passa a impedir esse tipo de regressão.

### 5.3 Lista de geradores

**Atualizar:**

| Linguagem | Gerador | Versão alvo |
|---|---|---|
| Go | hugo | 0.167.0 |
| JavaScript | gatsby | 5.16.x |
| JavaScript | metalsmith-handlebars | metalsmith 2.7.x (sai do WIP) |
| JavaScript | metalsmith-nunjucks | metalsmith 2.7.x (sai do WIP) |
| PHP | jigsaw | 1.8.8 |
| Python | nikola-mako | 8.3.3 |
| Ruby | jekyll | 4.4.1 |
| Ruby | nanoc | 4.14.8 (Gemfile reduzido a `nanoc`, `kramdown`, `erubi`; sai o grupo `:plugins`) |
| Ruby | middleman | 4.6.3 (sai do WIP) |

**Remover:** `JavaScript/harp-ejs`, `JavaScript/harp-jade`, `JavaScript/phenomic-react`, `JavaScript/cuttlebelle`, `Ruby/webgen`.

**Adicionar:**

| Linguagem | Gerador | Versão alvo | `content.type` | Pasta de conteúdo |
|---|---|---|---|---|
| Rust | zola | 0.23.6 | `3plus` | `content/posts` |
| JavaScript | astro | 7.3.x | `3minus` | `src/content/posts` |
| JavaScript | eleventy | 3.1.x | `3minus` | `posts` |
| JavaScript | hexo | 8.1.x | `3minus` | `source/_posts` |
| JavaScript | nextjs-export | 16.3.x | `3minus` | `content/posts` |
| JavaScript | vitepress | 1.6.x | `3minus` | `posts` |
| Python | pelican | 4.12.x | `3minus` | `content` |
| Python | mkdocs | 1.6.x | `none` | `docs/posts` |

Cada site novo tem só: um layout base, um template de post e uma página índice listando os posts, sem tema, plugins ou otimização de assets. As versões "x" são fixadas no lockfile no momento da implementação.

Total: 17 geradores em 6 linguagens.

### 5.4 `build.sh` canônico

Uma única versão, copiada idêntica para cada gerador. Partir da versão do monorepo e aplicar:

- Comparação de `content_size` sem colchetes (seção 4.2).
- Novo `content.type` `3plus`: front matter TOML

  ```
  +++
  title = "<title>"
  date = <YYYY-MM-DD>
  +++
  ```

- Remover os tipos `datajson` e `external`, usados só por Harp e Cuttlebelle.
- Novo campo opcional `config[].output_folder` + `config[].output_glob` no `benchmark_config.json`. Depois do primeiro build, `build.sh` conta os arquivos que batem com o glob; se forem menos que `number_of_files`, imprime `SSGBERK_VERIFY_FAIL expected=<n> got=<m>`. Se o campo não existir, a verificação é pulada (com aviso).
- `hyperfine` **sem** `--ignore-failure`, com `--export-json` e marcadores (seção 4.3), mais `STARTTIME`/`ENDTIME`.
- `delete_post` também limpa o `output_folder` antes de cada rodada (`--prepare`), para que builds incrementais não mascarem o tempo.

O CI do `ssg-frameworks` falha se algum `*/*/build.sh` diferir do canônico (compara todos com `Go/hugo/build.sh`).

## 6. Validação

### 6.1 Unitários (`benchmark-tool`, `pytest`)

- `DockerHelper.benchmark` grava a saída do container no `raw.txt` byte a byte (sem `log()`), porque os chunks de `logs(stream=True)` não respeitam limites de linha e o `log()` insere quebras que corromperiam o JSON.
- `Results.parse_test`:
  - `raw.txt` com marcadores e JSON válido → 1 resultado com `mean`, `stddev`, `min`, `max`, `times`.
  - Sem marcadores → `[]`.
  - JSON inválido entre marcadores → `[]`.
  - Contém `SSGBERK_VERIFY_FAIL` → `[]`.
- `Results.__parse_stats` com um CSV real do `dool` gravado como fixture.
- `run-tests.py`: `-cs 100000` aceito como string única; `-cs 7` rejeitado; default `0.500`; `-v` sem valor → `True`.
- `python3 -m compileall -q toolset` sem erros.

### 6.2 Smoke test por gerador

`./ssgberk --test <nome> -nf 10 -cs 500 -mr 1` deve:

1. construir a imagem (amd64 no CI; arm64 local e no runner `ubuntu-24.04-arm`);
2. gerar 10 posts e construir o site com código de saída 0;
3. passar na verificação de saída (seção 5.4);
4. aparecer em `succeeded.datarate` do `results.json` com `mean > 0`.

### 6.3 CI

- `benchmark-tool`: `compileall`, `ruff`, `pytest`; em PR, smoke test de `hugo` (prova toolset + submodule).
- `ssg-frameworks`: check de `build.sh` idênticos; smoke test em matriz só para os geradores alterados, em `ubuntu-24.04` e `ubuntu-24.04-arm`. O workflow faz checkout do `benchmark-tool` e coloca o repo atual em `frameworks/`.

## 7. Ordem de entrega

Cada passo é um PR independente com CI verde. Trabalho no branch `chore/modernize-2026` de cada repo, em worktrees isolados; commits assinados (GPG `B6FA8458D5176E83`).

1. **benchmark-tool:** Dockerfile do toolset + port Py3 + renomeação de imagens + unitários.
2. **benchmark-tool:** contrato de resultados (4.3) + CI + Vagrant + README + `package.json`.
3. **ssg-frameworks:** `build.sh` canônico + dockerfile base + `Go/hugo`, validado de ponta a ponta com o toolset do passo 2.
4. **ssg-frameworks:** atualizar os outros 5 geradores ativos (gatsby, jigsaw, nikola-mako, jekyll, nanoc), atualizar e ativar os 3 do WIP (metalsmith-handlebars, metalsmith-nunjucks, middleman), remover os 5 mortos.
5. **ssg-frameworks:** adicionar os 8 novos (1 commit por gerador).
6. **benchmark-tool:** bump do submodule + rodada completa + `docs/results/example-2026-10.json`.

Ao final: `git worktree remove` + `git worktree prune` nos dois repos. Os ~85 branches abertos do dependabot ficam obsoletos; fechá-los só com aprovação explícita.

## 8. Riscos e notas de medição

- **Bundlers dominam o tempo de geradores JS "app-like" (Gatsby, Next.js, Astro, VitePress) com poucos arquivos.** É o comportamento real deles; fica documentado no README, sem ajuste.
- **Gems nativas em Ruby 3.2 (Middleman, Nanoc):** se não compilarem, o gerador volta para `frameworks_WIP/` com o motivo no README dele, sem bloquear os demais. O critério de sucesso 1 passa a contar os geradores restantes, e a exceção é registrada no PR.
- **Ruído no Docker Desktop (macOS):** números locais servem para validar, não para publicar; resultados oficiais vêm de Linux nativo.
- **Cenários grandes (`-nf 1000000`) em `build.sh` bash:** a geração de conteúdo via loop + `sponge` é lenta. Mantida no port mínimo; registrada como melhoria futura.

## 9. Fora de escopo

- Reescrever o toolset ou trocar a geração de conteúdo para Python.
- Temas, plugins ou otimizações específicas de algum gerador.
- Site de resultados (`ssgberk.matheusrv.com`).
- O monorepo `StaticSiteGeneratorBenchmark`.
