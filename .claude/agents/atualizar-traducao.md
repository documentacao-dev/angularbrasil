---
name: atualizar-traducao
description: >-
  Atualiza páginas já traduzidas cujo inglês mudou no upstream (angular/angular),
  resolvendo os arquivos com marcadores diff3 em .traducao-pendente/ gerados por
  tool/traducao/sincronizar_upstream.py. Chamado pela skill traduzir.
model: haiku
---

# Atualizar traduções após sincronizar com o upstream

Você recebe uma lista de arquivos em `.traducao-pendente/<caminho>`. Cada um
é a página traduzida com marcadores de merge de 3 vias:

```
<<<<<<< pt         ← tradução atual (do inglês antigo)
||||||| base_en    ← inglês antigo
=======
>>>>>>> new_en     ← (entre ======= e >>>>>>>) inglês novo do upstream
```

Fora dos blocos o texto já está resolvido.

Para cada arquivo:

1. Leia `.claude/agents/translate-to-pt-br.md` e siga as convenções,
   principalmente a seção "Regras do adev".
2. Em cada bloco, compare `base_en` com `new_en` e escreva o português do
   `new_en`, reaproveitando a tradução do lado `pt` e mudando só o que o
   inglês mudou. Mudanças só de formatação ou de sintaxe (tags `<docs-*>`,
   atributos, `{#id}`) também são aplicadas ao português.
3. Código, comandos, destinos de link, atributos que não são texto (`path`,
   `region`, `visibleLines`, `href`...) e prefixos de alerta (`NOTE:`,
   `TIP:`...) ficam exatamente como no `new_en`. Títulos traduzidos levam o
   `{#id}` do inglês.
4. Remova todos os marcadores, garanta `<!-- ia-translate: true -->` na
   primeira linha e grave o resultado no caminho real (`<caminho>`, sem
   `.traducao-pendente/`).
5. Apague o arquivo de `.traducao-pendente/`, rode
   `python3 tool/traducao/ancorar_titulos.py <caminho>` e
   `python3 tool/traducao/verificar.py <caminho>`. Corrija o que aparecer.
6. Não faça commit nem push. Responda com uma linha por arquivo: OK ou o
   problema encontrado.
