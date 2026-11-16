---
name: traduzir
description: >-
  Roda o ciclo completo de tradução do Angular Brasil de ponta a ponta: sync de
  adev/src/content/ com o upstream (angular/angular), retradução das páginas que
  mudaram e tradução das páginas novas em subagentes Haiku, verificação
  determinística, commit, PR, review independente em Sonnet, correção em Haiku e
  auto-merge quando tudo fica verde. Use quando pedirem "traduzir",
  "sincronizar com o upstream", "rodar o sync", "atualizar a tradução", "o
  inglês mudou", "tem página defasada", ou quando a rotina semanal na nuvem ou o workflow
  traducao-automatica.yml chamar. Também serve para traduzir só um conjunto de
  páginas: passe os caminhos como argumento.
---

# Ciclo de tradução do Angular Brasil

Você é o **orquestrador**. Quem traduz é sempre um subagente **Haiku**; quem
revisa é um subagente **Sonnet** de contexto limpo. Você não escreve tradução:
cuida de git, scripts, lotes, commits, PR e da decisão de merge.

Argumentos opcionais (`$ARGUMENTS`): caminhos de páginas para traduzir só
elas, ou `sem-merge` para parar no PR pronto, sem auto-merge.

Leia antes: `CLAUDE.md` (processo e scripts de `tool/traducao/`) e as
convenções em `.claude/agents/translate-to-pt-br.md`.

## 0. Ambiente

```console
bash tool/traducao/setup.sh     # remote upstream, fetch parcial, blobs de adev/src/content
```

Só git e python3. Não rode `pnpm install` nem Bazel: o build do site fica
com o workflow `firebase-deploy.yml`, que roda no PR.

**Branch já preparada pelo workflow.** No Actions, a fase `preparar` do
`traducao-automatica.yml` já detectou o trabalho, rodou o sync, o
`gerar_todo.py` e o `verificar.py`, e publicou a branch `traducao/AAAA-MM-DD`.
Nesse caso, comece na etapa 3 e não rode o `sincronizar_upstream.py` de novo.

Árvore limpa e `main` atualizada. Se já existir um PR aberto com o label
`traducao-automatica`, **não abra outro**: continue nele (faça checkout da
branch dele e pule para a etapa que faltar).

## 1. Detectar o que fazer

- `git rev-list --count $(cat tool/traducao/ultimo-sync-upstream.txt)..upstream/main -- adev/src/content`
  diz quantos commits do upstream mexeram nas docs desde o último sync.
- `TODO-TRADUCAO.md` lista as páginas ainda não traduzidas.
- Se não há commit novo do upstream nem página pendente (e nenhum caminho foi
  passado), **pare aqui** e responda "nada a traduzir". Não abra PR vazio.

Crie a branch `traducao/AAAA-MM-DD` a partir da `main`.

## 2. Sync com o upstream

Siga a "Regra principal" do `CLAUDE.md`, passos 2 e 3: rode
`python3 tool/traducao/sincronizar_upstream.py` e faça o commit
**incluindo** `.traducao-pendente/`. O sync só mexe em `adev/src/content/`
e não é um merge do upstream (veja o `CLAUDE.md`).

Arquivos de `.traducao-pendente/` que não são prosa (`.ts`, `.html`,
`.json` dos exemplos e tutoriais) você resolve direto, sem agente: quase
sempre é ficar com o `new_en` e manter as strings que o fork traduziu.

## 3. Traduzir em Haiku

Monte lotes equilibrados por tamanho, **no máximo 5 subagentes em paralelo**,
nunca dois no mesmo arquivo. Sempre com `model: "haiku"` na ferramenta Agent:

- Páginas em `.traducao-pendente/` → subagente com o prompt de
  `.claude/agents/atualizar-traducao.md`.
- Páginas novas (do `TODO-TRADUCAO.md` ou dos argumentos) → subagente com o
  prompt de `.claude/agents/translate-to-pt-br.md`.
- Páginas em que o inglês só mudou um atributo, um link ou um trecho de
  código: resolva por script, sem tradução.

Depois: `python3 tool/traducao/ancorar_titulos.py <arquivos traduzidos>` e,
com `.traducao-pendente/` vazio (só o `RELATORIO.md`), apague a pasta e rode
`python3 tool/traducao/gerar_todo.py`.

## 4. Verificar

```console
python3 tool/traducao/verificar.py
```

Zero erros é obrigatório (avisos `orfa` são de arquivos antigos do fork e não
bloqueiam). Erro num arquivo traduzido volta para um subagente Haiku com a
saída do `verificar.py` no prompt (no máximo 2 tentativas por arquivo; depois
corrija o trecho você mesmo, sem trocar de modelo). Procure também prosa em
inglês que escapou do limite de 30% (avisos `parcial`, e seções novas
inteiras em inglês nos arquivos "mesclados automaticamente" do
`RELATORIO.md`) e mande para o Haiku.

## 5. Commit e PR

- Commits por lote, mensagens em português
  (`chore: sync de adev/src/content com upstream <sha>`,
  `docs(pt-br): retraduz ...`, `docs(pt-br): traduz ...`).
- `git push -u origin traducao/AAAA-MM-DD`
- `gh pr create --base main --label traducao-automatica` com o corpo:
  commits do upstream (de → para), páginas retraduzidas, páginas novas,
  resolvidas por script, e o que ficou de fora.

## 6. Review em Sonnet (contexto limpo)

Dispare o subagente `revisar-traducao` (`.claude/agents/revisar-traducao.md`,
`model: "sonnet"`) passando **só** a lista de arquivos traduzidos ou alterados
neste ciclo e o commit do upstream. Não passe sua opinião nem o resumo do que
foi feito. Lotes de no máximo **~1.500 linhas por revisor**, até 5
revisores em paralelo.

Cada revisor termina com `COBERTURA: <x>% da prosa lida lado a lado`. Se
algum declarar cobertura abaixo de 100% (ou não declarar), o pedaço que
faltou volta para **outro** revisor antes da etapa 8. Review sem 100% de
cobertura não conta como OK.

O revisor devolve, por arquivo, `OK` ou problemas classificados como
**grave** (sentido trocado, trecho faltando, código/link/âncora/atributo
alterado, inglês sem tradução) ou **leve** (estilo, escolha de palavra).

Publique o resultado como um comentário no PR (`gh pr comment`), uma linha
por arquivo com problema.

## 7. Corrigir em Haiku

Problemas **graves** voltam para subagentes Haiku com o apontamento do
revisor no prompt. Leves só se forem baratos. Depois, `verificar.py` de novo,
commit `fix(pt-br): correções do review`, push, e um **novo review só dos
arquivos corrigidos**. No máximo 2 voltas de review + correção.

## 8. Aprovação e merge

Auto-merge **só** se as três condições valerem:

1. `verificar.py` com 0 erros;
2. o último review sem nenhum problema grave em aberto e com 100% de cobertura;
3. o argumento `sem-merge` não foi passado.

Então:

```console
gh pr edit <n> --add-label revisao-ok
gh pr merge <n> --auto --squash --delete-branch
```

O auto-merge espera os checks obrigatórios da `main`. Hoje a `main` do fork
não exige nenhum, então o merge aconteceria na hora: **antes** de ligar o
auto-merge, espere o build do site com `gh pr checks <n> --watch --fail-fast`
(o job `Build and Deploy to Firebase` compila o adev com Bazel e demora). Build
vermelho conta como condição falha.

Se alguma condição falhar: `gh pr edit <n> --add-label precisa-humano`, um
comentário dizendo exatamente o que ficou pendente, e **sem** auto-merge.

## 9. Resposta final

Uma mensagem curta: link do PR, de qual para qual commit do upstream, quantas
páginas retraduzidas / novas / por script, resultado do review (graves e
leves), e se ficou em auto-merge ou com `precisa-humano`.
