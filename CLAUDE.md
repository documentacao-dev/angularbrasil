# CLAUDE.md — Angular Brasil

Este repositório é a tradução para português do Brasil da documentação do
Angular (angular.dev), publicada em <https://angularbrasil.dev>. É um fork do
[angular/angular](https://github.com/angular/angular) (remote `upstream`),
parte da org [`documentacao-dev`](https://github.com/documentacao-dev). O
contexto técnico do framework está no `AGENTS.md` do upstream:

@AGENTS.md

## Começando do zero (sessão nova)

```console
bash tool/traducao/setup.sh
```

O script adiciona o remote `upstream` (angular/angular), busca o histórico
com `--filter=blob:none` (e `--depth` só em clone raso: nunca use `--depth`
num clone completo, ele deixa o repositório inteiro raso) e baixa os arquivos
de `adev/src/content/` do último sync e do upstream atual. O ciclo de
tradução só precisa de git e python3. O build do site (pnpm + Bazel, pesado)
roda no workflow `firebase-deploy.yml`, em todo PR.

## Agentes e paralelismo

- **No máximo 5 agentes em paralelo.** Lotes equilibrados por tamanho, sem
  dois agentes no mesmo arquivo. Agentes não fazem commit nem push: quem
  orquestra confere com `verificar.py`, faz o commit por lote e o push.
- **Traduzir páginas novas:** agente `translate-to-pt-br`
  (`.claude/agents/translate-to-pt-br.md`, modelo **Haiku**). O portão de
  qualidade é o `verificar.py`; se um arquivo falhar duas vezes, refaça-o no
  Haiku com o erro no prompt ou corrija o trecho à mão na orquestração. Não
  troque de modelo.
- **Atualizar páginas já traduzidas** (arquivos diff3 de
  `.traducao-pendente/`): agente `atualizar-traducao`
  (`.claude/agents/atualizar-traducao.md`, modelo **Haiku**).
- **Review:** agente `revisar-traducao` (`.claude/agents/revisar-traducao.md`,
  modelo **Sonnet**), de contexto limpo, que só aponta.
- Código (`.ts`, `.html` dos exemplos, componentes do site), workflows e
  configuração: resolva diretamente, sem agente.

## Onde fica o quê

- `adev/src/content/`: páginas em Markdown (o que se traduz), inclusive os
  `README.md` dos passos dos tutoriais.
- `adev/src/app/routing/navigation-entries/index.ts`: menu lateral (rótulos
  traduzidos). `adev/src/app/core/layout/` e `adev/src/app/features/home/`:
  rodapé, navegação e home traduzidos.
- `adev/shared-docs/pipeline/`: o renderizador do Markdown (ids de título em
  `shared/heading.mts`, alertas em `marked/extensions/docs-alert.mts`, tags
  pareadas em `marked/validate-paired-tags.mts`).
- `.claude/agents/translate-to-pt-br.md`: **convenções de tradução**. Siga
  sempre.
- `tool/traducao/`: scripts de tradução e de sincronização (abaixo).
- `TODO-TRADUCAO.md`: status das páginas, gerado. Substitui
  `FILES_TO_MIGRATE.txt`, `UNTRANSLATED_FILES.txt` e `plan/`, que ficam como
  histórico.

## Regras de tradução (resumo)

As regras completas estão em `.claude/agents/translate-to-pt-br.md`. As mais
importantes:

- Página traduzida tem `<!-- ia-translate: true -->` na **primeira linha**.
  Não há cópia em inglês no fork: o original é
  `git show upstream/main:<caminho>`.
- Títulos `##`+ e `<docs-step title>` traduzidos levam o id em inglês:
  `## Criando um component {#creating-a-component}`. O H1 não leva id.
- Prefixos de alerta ficam em inglês (`NOTE:`, `TIP:`, `IMPORTANT:`,
  `CRITICAL:`, `HELPFUL:`...); o renderizador não reconhece `NOTA:`.
- Tags `<docs-*>` idênticas ao inglês; só os atributos de texto (`title`,
  `header`, `label`, `description`, `headerTitle`, `link`) são traduzidos.
- Não traduza código, comandos nem destinos de link.
- Termos técnicos consagrados ficam em inglês (component, service, signal,
  template, pipe, directive, build etc.).

## Ciclo automático: skill `traduzir`

O ciclo inteiro (sync, tradução, verificação, commit, PR, review, correção e
auto-merge) está na skill `.claude/skills/traduzir/SKILL.md`. Rode `/traduzir`
numa sessão local ou na web; o workflow `traducao-automatica.yml` roda a mesma
skill toda segunda às 11h UTC e por disparo manual (Actions → Tradução
automática, com os campos `paginas` e `sem_merge`).

No workflow, as etapas determinísticas rodam **sem Claude**, na fase
`preparar`: detectar commits novos do upstream em `adev/src/content/` e
páginas pendentes (sem nada, o workflow para com custo zero), sync,
`gerar_todo.py` e `verificar.py`. O Claude só entra depois, na branch já
sincronizada, para traduzir, abrir o PR, revisar e ligar o merge.

- Tradução e correção: subagentes **Haiku**. Review: `revisar-traducao` em
  **Sonnet**.
- Auto-merge só com `verificar.py` zerado, review sem problema grave e build
  do site verde; senão o PR fica com o label `precisa-humano`.
- O workflow precisa do secret `CLAUDE_CODE_OAUTH_TOKEN`.

## Regra principal: manter as traduções em dia com o upstream

**Traduzir páginas novas não basta: toda página já traduzida precisa ser
atualizada sempre que o inglês dela mudar no upstream.** Uma página com
`<!-- ia-translate: true -->` defasada em relação ao inglês atual é um bug
(o `verificar.py` acusa como `defasada`).

O sync **não é um `git merge` do angular/angular**: o repositório é quase todo
o framework, e trazê-lo inteiro a cada semana é caro e quebra o build do
fork. O script traz só `adev/src/content/` (prefixos extras com `--escopo`,
ex.: `--escopo adev/src/content/ adev/src/app/` quando uma mudança do site for
necessária) e grava um commit comum. O commit do upstream incorporado fica em
`tool/traducao/ultimo-sync-upstream.txt`.

Em toda sincronização:

1. `bash tool/traducao/setup.sh` e crie uma branch.
2. Rode `python3 tool/traducao/sincronizar_upstream.py`. Ele:
   - troca `adev/src/content/` pela árvore do upstream (páginas novas entram,
     apagadas saem, renomeadas mudam de lugar);
   - copia a tradução quando o inglês não mudou;
   - faz merge de 3 vias quando mudou. Sem conflito, grava o resultado. Com
     conflito, grava em `.traducao-pendente/<caminho>` com marcadores diff3
     e deixa o inglês novo no repositório (sem a marca);
   - mantém os arquivos que só existem no fork;
   - grava `.traducao-pendente/RELATORIO.md` e atualiza
     `ultimo-sync-upstream.txt`.
3. Faça o commit **incluindo** `.traducao-pendente/`, para nada se perder
   entre sessões.
4. Resolva **todos** os arquivos de `.traducao-pendente/`:
   - em cada bloco `<<<<<<< pt` / `||||||| base_en` / `=======` / `>>>>>>> new_en`,
     escreva o português do `new_en`, reaproveitando a tradução do lado `pt`
     e mudando só o que o inglês mudou;
   - grave no caminho real, com `<!-- ia-translate: true -->` na 1ª linha;
   - apague o arquivo resolvido de `.traducao-pendente/`.
5. Confira os "mesclados automaticamente" do relatório: linhas novas do
   inglês podem ter entrado sem tradução.
6. Rode `ancorar_titulos.py` nas páginas resolvidas e `verificar.py`.
7. Com `.traducao-pendente/` vazio, apague a pasta, rode `gerar_todo.py` e
   faça o commit.
8. Só depois siga para as páginas novas (`TODO-TRADUCAO.md`).

Nunca resolva um conflito trocando a página pela versão em inglês e mantendo
a marca, nem descartando o texto novo do upstream.

## Scripts de `tool/traducao/`

| Script | Para quê |
|---|---|
| `setup.sh` | Remote `upstream`, fetch parcial e blobs de `adev/src/content/`. |
| `sincronizar_upstream.py [--alvo] [--escopo]` | Sync do conteúdo com o upstream preservando traduções (acima). |
| `verificar.py [--estrito] [arquivos]` | **Checagens determinísticas** (abaixo). Sem argumentos confere todas as páginas marcadas. |
| `ancorar_titulos.py <arquivos>` | Acrescenta `{#id}` em inglês aos títulos e `<docs-step>` traduzidos (porte do `getIdFromHeading` do adev). Rode em toda página traduzida. |
| `gerar_todo.py` | Regenera `TODO-TRADUCAO.md`. |

## Checagens determinísticas

```console
python3 tool/traducao/verificar.py
```

**Erros**: `conflito` (marcadores de merge), `flag` (marca ausente ou fora
da 1ª linha), `placeholder`, `ingles` (70%+ da prosa em inglês),
`estrutura` (cercas, tags `<docs-*>`, âncoras `{#id}` ou títulos diferentes
do inglês), `tags` (tag pareada sem fechar: derruba o build), `atributos`
(`path`, `region`, `href`, `visibleLines`... diferentes do inglês), `alerta`
(prefixo traduzido ou faltando), `link` (destino só num dos idiomas; MDN
pt-BR é aceito), `ancora` (título traduzido sem `{#id}` do inglês),
`id-duplicado`, `link-interno` (âncora da própria página inexistente),
`defasada` (o inglês mudou desde o último sync), `pendente`
(`.traducao-pendente/` com arquivos) e `workflow` (workflow do ciclo ausente
ou preso a outro repositório; usa `REPO_FORK`).

**Avisos** (só falham com `--estrito`): `parcial` (30% a 70% em inglês) e
`orfa` (arquivo marcado que não existe no upstream, como as cópias antigas em
pastas `pt-br/`).

Quando uma checagem nova pegar um caso que escapou, acrescente-a ao
`verificar.py` em vez de corrigir só o arquivo.

## Git

- Trabalhe em branch e abra PR para a `main`.
- Commits em português: `docs(pt-br): traduz <caminho>`, sync:
  `chore: sync de adev/src/content com upstream angular/angular <sha>`.

## Modelo da tradução: sempre Haiku

Toda tradução e retradução de página (tradução nova, sync com o upstream, revisão de trecho) roda no **Haiku** (`model: haiku`, hoje Claude Haiku 5.5), local ou na nuvem (Claude Code na web, GitHub App, rotinas agendadas).

- Os agentes em `.claude/agents/` já declaram `model: haiku`. Não troque.
- Se um orquestrador disparar subagentes para traduzir, passe `model: "haiku"` na ferramenta Agent.
- O modelo principal da sessão fica só com a orquestração: merge do upstream, scripts de conferência, commits e PR. Ele não traduz páginas.
- Exceção: o **review** (agente `revisar-traducao`) roda em **Sonnet**. Ele só aponta problemas; quem corrige é o Haiku.
