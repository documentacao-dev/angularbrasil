#!/usr/bin/env python3
"""Gera TODO-TRADUCAO.md com o status de tradução das páginas do adev.

Uma página de adev/src/content/ conta como traduzida quando a primeira linha
é `<!-- ia-translate: true -->`. Arquivos que não existem no upstream (commit
de tool/traducao/ultimo-sync-upstream.txt) são listados à parte, como órfãos,
e não entram na contagem. Execute a partir da raiz do repositório:

    python3 tool/traducao/gerar_todo.py
"""
from collections import defaultdict
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / 'adev' / 'src' / 'content'
SAIDA = ROOT / 'TODO-TRADUCAO.md'
CABECALHO = ROOT / 'tool' / 'traducao' / 'todo_cabecalho.md'
SYNC = ROOT / 'tool' / 'traducao' / 'ultimo-sync-upstream.txt'
FLAG = '<!-- ia-translate: true -->'
# Seções grandes ganham subseção (guide/forms, reference/errors...).
SUBDIVIDIR = ('guide', 'reference', 'tutorials', 'tools', 'ecosystem')
# Seções de baixa prioridade ficam no fim da lista.
BAIXA_PRIORIDADE = ('reference/errors', 'reference/extended-diagnostics')


def no_upstream():
    """Caminhos .md de adev/src/content/ no último sync, ou None se o commit
    não estiver disponível (clone raso sem o upstream)."""
    if not SYNC.exists():
        return None
    r = subprocess.run(['git', '-C', str(ROOT), 'ls-tree', '-r', '--name-only',
                        SYNC.read_text().strip(), '--', 'adev/src/content/'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return {p[len('adev/src/content/'):] for p in r.stdout.split() if p.endswith('.md')}


def secao_de(rel):
    partes = rel.split('/')
    if len(partes) == 1:
        return '(raiz)'
    if partes[0] in SUBDIVIDIR and len(partes) > 2:
        return '/'.join(partes[:2])
    return partes[0]


def main() -> None:
    upstream = no_upstream()
    secoes, orfas = defaultdict(list), []
    total = traduzidas = linhas_pendentes = 0
    for md in sorted(CONTENT.rglob('*.md')):
        rel = md.relative_to(CONTENT).as_posix()
        texto = md.read_text(encoding='utf-8')
        if upstream is not None and rel not in upstream:
            orfas.append(rel)
            continue
        ok = texto.startswith(FLAG)
        n = texto.count('\n')
        total += 1
        traduzidas += ok
        linhas_pendentes += 0 if ok else n
        secoes[secao_de(rel)].append((rel, ok, n))

    def chave(s):
        return (s in BAIXA_PRIORIDADE, s)

    out = [CABECALHO.read_text(encoding='utf-8').rstrip(), '']
    pct = 100 * traduzidas / total if total else 0
    out += ['## Progresso', '',
            f'- Páginas traduzidas: **{traduzidas} / {total}** ({pct:.1f}%)',
            f'- Linhas pendentes (aprox.): {linhas_pendentes}', '',
            '| Seção | Traduzidas | Total |', '|---|---:|---:|']
    for s in sorted(secoes, key=chave):
        itens = secoes[s]
        out.append(f'| `{s}` | {sum(i[1] for i in itens)} | {len(itens)} |')
    out += ['', '## Páginas por seção', '']
    for s in sorted(secoes, key=chave):
        itens = secoes[s]
        out += [f'### `{s}` ({sum(i[1] for i in itens)}/{len(itens)})', '']
        out += [f'- [{"x" if ok else " "}] `{rel}` ({n} linhas)' for rel, ok, n in itens]
        out.append('')
    if orfas:
        out += ['## Arquivos sem original no upstream', '',
                'Existem só no fork (restos de traduções antigas, como as pastas',
                '`pt-br/`). Não contam no progresso; apague ou mova para o caminho',
                'certo.', '']
        out += [f'- `{rel}`' for rel in orfas]
        out.append('')
    SAIDA.write_text('\n'.join(out), encoding='utf-8')
    print(f'{SAIDA.name}: {traduzidas}/{total} traduzidas'
          + (f', {len(orfas)} órfão(s)' if orfas else ''))


if __name__ == '__main__':
    main()
