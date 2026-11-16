#!/usr/bin/env python3
"""Sincroniza o conteúdo de docs deste repositório com o upstream
(angular/angular) preservando as traduções e marcando o que precisa ser
retraduzido.

Uso (a partir da raiz do repositório, com a árvore limpa):

    bash tool/traducao/setup.sh          # remote upstream + fetch parcial
    python3 tool/traducao/sincronizar_upstream.py [--alvo upstream/main]
                                                  [--escopo adev/src/content/ ...]

O angular/angular é enorme e quase todo ele é o framework, não a
documentação. Por isso o sync NÃO é um `git merge` do upstream inteiro: ele
só traz os caminhos do escopo (por padrão `adev/src/content/`) e o resultado é
um commit comum, sem o upstream como pai. O ponto de partida fica registrado
em tool/traducao/ultimo-sync-upstream.txt.

O que o script faz:

1. Lê o último commit do upstream já sincronizado em
   tool/traducao/ultimo-sync-upstream.txt (a "base").
2. Troca o escopo pela árvore exata do upstream no alvo (arquivos novos
   entram, apagados saem, renomeados mudam de lugar).
3. Para cada arquivo do escopo que o Angular Brasil alterou em relação à base:
   - descobre o caminho novo (mesmo caminho ou renomeação detectada pelo git);
   - se o original em inglês não mudou, copia a versão do Angular Brasil;
   - se mudou, faz merge de 3 vias (versão BR, inglês base, inglês novo).
     Sem conflito, grava o resultado. Com conflito, grava o arquivo com
     marcadores diff3 em .traducao-pendente/<caminho novo> e deixa o
     inglês novo no lugar, SEM o `<!-- ia-translate: true -->` (a página
     volta a aparecer como pendente no TODO).
   - arquivo que só existe no fork (não está na base nem no alvo) é mantido.
4. Grava o relatório em .traducao-pendente/RELATORIO.md e atualiza
   ultimo-sync-upstream.txt para o alvo.

Depois: faça o commit (incluindo .traducao-pendente/), resolva cada arquivo
de .traducao-pendente/ (veja CLAUDE.md), rode tool/traducao/verificar.py,
apague .traducao-pendente/ e faça o commit.

`--escopo` aceita outros prefixos (ex.: `adev/src/app/` para trazer também
mudanças do site). Os arquivos do Angular Brasil nesses prefixos (navegação,
rodapé, home traduzidos) passam pelo mesmo merge de 3 vias.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SYNC = ROOT / 'tool' / 'traducao' / 'ultimo-sync-upstream.txt'
PEND = ROOT / '.traducao-pendente'
ESCOPO_PADRAO = ['adev/src/content/']
FLAG = b'<!-- ia-translate: true -->'


def git(*args, check=True):
    r = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f'git {" ".join(args)} falhou:\n{r.stderr}')
    return r.stdout


def show(ref, caminho):
    r = subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:{caminho}'],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--alvo', default='upstream/main')
    ap.add_argument('--escopo', nargs='+', default=ESCOPO_PADRAO)
    a = ap.parse_args()
    escopo = [e.rstrip('/') + '/' for e in a.escopo]

    if git('status', '--porcelain').strip():
        sys.exit('A árvore de trabalho precisa estar limpa.')
    base = SYNC.read_text().strip()
    alvo = git('rev-parse', a.alvo).strip()
    if base == alvo:
        sys.exit('Já sincronizado com ' + alvo)
    if git('cat-file', '-e', base + '^{commit}', check=False) is None:
        sys.exit(f'Commit base {base[:9]} não encontrado: rode bash tool/traducao/setup.sh '
                 '(ou aumente o --depth do fetch do upstream).')
    head = git('rev-parse', 'HEAD').strip()

    # Baixa de uma vez os blobs do escopo (clone parcial) antes dos `git show`.
    git('diff', '--stat', base, alvo, '--', *escopo)
    git('diff', '--stat', base, head, '--', *escopo)

    arquivos_alvo = set(git('ls-tree', '-r', '--name-only', alvo, '--', *escopo).split())
    renomes = {}
    for linha in git('-c', 'diff.renameLimit=50000', 'diff', '-M70%', '--name-status',
                     base, alvo, '--', *escopo).splitlines():
        partes = linha.split('\t')
        if partes[0].startswith('R'):
            renomes[partes[1]] = partes[2]

    def caminho_novo(p):
        if p in arquivos_alvo:
            return p
        if p in renomes and renomes[p] in arquivos_alvo:
            return renomes[p]
        return None

    alterados = [l.split('\t') for l in git('diff', '--name-status', '--no-renames',
                                             base, head, '--', *escopo).splitlines()]
    alterados = [(s, p) for s, p in alterados if s in ('M', 'A')]
    n_commits = git('rev-list', '--count', f'{base}..{alvo}', '--', *escopo,
                    check=False).strip() or '?'
    print(f'Base {base[:9]} → alvo {alvo[:9]} ({n_commits} commit(s) no escopo); '
          f'{len(alterados)} arquivo(s) do Angular Brasil no escopo.')

    # O escopo passa a ser exatamente o do upstream.
    for e in escopo:
        if git('ls-files', '--', e).strip():
            git('rm', '-r', '-q', '--', e)
        if any(p.startswith(e) for p in arquivos_alvo):
            git('checkout', alvo, '--', e)

    copiados, mesclados, conflitos, sem_destino, exclusivos = [], [], [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for _, p in alterados:
            br = show(head, p)
            en_base = show(base, p)
            n = caminho_novo(p)
            if n is None:
                if en_base is None:  # arquivo exclusivo do Angular Brasil
                    (ROOT / p).parent.mkdir(parents=True, exist_ok=True)
                    (ROOT / p).write_bytes(br)
                    exclusivos.append(p)
                else:
                    sem_destino.append(p)
                continue
            en_novo = show(alvo, n)
            if en_base == en_novo or en_base is None:
                (ROOT / n).write_bytes(br)
                copiados.append(n)
                continue
            (tmp / 'br').write_bytes(br)
            (tmp / 'base').write_bytes(en_base)
            (tmp / 'novo').write_bytes(en_novo)
            r = subprocess.run(['git', 'merge-file', '-p', '--diff3', '-L', 'pt',
                                '-L', 'base_en', '-L', 'new_en', str(tmp / 'br'),
                                str(tmp / 'base'), str(tmp / 'novo')],
                               capture_output=True)
            if r.returncode == 0:
                (ROOT / n).write_bytes(r.stdout)
                mesclados.append(n)
            else:
                destino = PEND / n
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(r.stdout)
                conflitos.append((n, r.stdout.count(b'\n<<<<<<< pt')
                                  + r.stdout.startswith(b'<<<<<<< pt')))
    git('add', '-A', '--', *escopo)

    SYNC.write_text(alvo + '\n')
    PEND.mkdir(exist_ok=True)
    rel = [f'# Sincronização {base[:9]} → {alvo[:9]}', '',
           f'Escopo: {", ".join(f"`{e}`" for e in escopo)} '
           f'({n_commits} commit(s) do upstream).', '',
           f'- Copiados sem mudança no inglês: {len(copiados)}',
           f'- Mesclados automaticamente: {len(mesclados)}',
           f'- **Com conflito (retraduzir)**: {len(conflitos)}',
           f'- Removidos no upstream: {len(sem_destino)}',
           f'- Exclusivos do Angular Brasil (mantidos): {len(exclusivos)}', '',
           '## Com conflito', '',
           'Cada arquivo abaixo está em `.traducao-pendente/<caminho>` com marcadores',
           'diff3 (`pt` / `base_en` / `new_en`). No repositório ficou o inglês novo.', '']
    rel += [f'- [ ] `{n}` ({c} bloco(s))' for n, c in sorted(conflitos)]
    rel += ['', '## Mesclados automaticamente', '',
            'O merge de 3 vias não deu conflito, mas linhas novas do inglês podem',
            'ter entrado sem tradução: confira com `verificar.py` (avisos `parcial`).', '']
    rel += [f'- `{n}`' for n in sorted(mesclados)]
    rel += ['', '## Removidos no upstream', '',
            'Não existem mais. Se a página nova que os substitui ainda não está',
            'traduzida, a tradução antiga pode servir de referência',
            f'(`git show {head[:9]}:<caminho>`).', '']
    rel += [f'- `{p}`' for p in sorted(sem_destino)]
    rel += ['', '## Páginas novas do upstream', '',
            'Ficaram em inglês, sem a marca; aparecem no `TODO-TRADUCAO.md`.', '']
    rel += [f'- `{p}`' for p in sorted(arquivos_alvo - set(git(
        'ls-tree', '-r', '--name-only', base, '--', *escopo).split())
        - set(renomes.values())) if p.endswith('.md')]
    (PEND / 'RELATORIO.md').write_text('\n'.join(rel) + '\n')
    print('\n'.join(rel[:10]))
    print('\nRelatório: .traducao-pendente/RELATORIO.md')


if __name__ == '__main__':
    main()
