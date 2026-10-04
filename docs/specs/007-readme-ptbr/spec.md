# 007 - README em pt-BR

## O que e por que
A secao "Português do Brasil" do `README.md` e uma traducao automatica antiga: termos errados
("janela de encaixe" para Docker, "recipiente" para container, "errante" para Vagrant), `-V` no lugar
de `-v`, links quebrados por causa do espaco entre `]` e `(`, e `$./ssgberk` sem espaco.

## Requisitos
1. Reescrever SOMENTE a secao em portugues, em pt-BR tecnico e natural, mantendo em ingles os termos
   usados pelos devs: container, Docker, Vagrant, worktree, benchmark, build.
2. Espelhar a secao em ingles 1:1: mesmos titulos na mesma ordem, mesmos comandos, tabela de tamanho
   de conteudo, notas de medicao e o credito ao TechEmpower.
3. Todos os links renderizam (sem espaco entre `]` e `(`); ancora do Vagrant valida.
4. Todos os comandos identicos aos da secao em ingles e validos contra `ssgberk`,
   `toolset/run-tests.py` (`build_parser`) e `deployment/vagrant/`.
5. Adicionar subsecao "Resultados" espelhando a "Results" da feature 006 (depende dela):
   `results/<timestamp>/` com `results.json`, `summary.csv` e `summary.md` (uma linha por gerador com
   media, desvio padrao, mediana, minimo e maximo, em segundos).
6. Sem HTML alem do `<p>` do cabecalho existente.

## Criterios de aceite
- Diff do README toca apenas a partir de `# Português do Brasil`.
- Nenhum `](` precedido de espaco; nenhum `] (` no arquivo.
- Comandos em blocos de codigo batem com os da secao em ingles.

## Fora de escopo
Secao em ingles, codigo, outros idiomas.
