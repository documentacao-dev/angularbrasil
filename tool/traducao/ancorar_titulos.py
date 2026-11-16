#!/usr/bin/env python3
"""Garante que cada título traduzido (`##` a `######`) e cada
`<docs-step title="...">` mantenha o id em inglês com `{#id}`.

O adev gera o id do título a partir do texto (ver
adev/shared-docs/pipeline/shared/heading.mts). Um título traduzido geraria um
id em português e quebraria os links `#ancora` vindos de outras páginas, do
upstream e da validação de âncoras do build. Por isso o id em inglês fica
explícito: `## Criando um component {#creating-a-component}`.

O título da página (H1) não leva id.

    python3 tool/traducao/ancorar_titulos.py [--ref upstream/main] arquivos...
"""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ID_CUSTOM = re.compile(r'\{#\s*([\w-]+)\s*\}')
PASSO = re.compile(r'(<docs-step\b[^>]*?\btitle=")([^"]*)(")')


def slug(texto):
    """Porte de getIdFromHeading (adev/shared-docs/pipeline/shared/heading.mts)."""
    m = ID_CUSTOM.search(texto)
    if m:
        return m.group(1)
    t = re.sub(r'[\s/]', '-', texto.lower())
    return ''.join(c for c in t if c.isalpha() or c in '0123456789-')


def titulos(texto):
    """[(índice_da_linha, nível, texto)] dos títulos `##+` fora de cercas."""
    res, em_codigo = [], False
    for i, linha in enumerate(texto.split('\n')):
        s = linha.strip()
        if s.startswith('```'):
            em_codigo = not em_codigo
            continue
        if not em_codigo and s.startswith('##'):
            nivel = len(s) - len(s.lstrip('#'))
            res.append((i, nivel, s[nivel:].strip()))
    return res


def passos(texto):
    """Títulos de `<docs-step>` em ordem: [(match)]."""
    return list(PASSO.finditer(texto))


def com_id(texto_pt, id_en):
    """Texto do título com o `{#id_en}` certo (ou None se não precisa)."""
    if not id_en or slug(texto_pt) == id_en:
        return None  # id explícito certo, ou o texto já gera o mesmo id
    sem = ID_CUSTOM.sub('', texto_pt).rstrip()
    return f'{sem} {{#{id_en}}}'


def ancorar(en, pt):
    """Retorna (texto_pt_ajustado, n_ajustes, problemas). `problemas` lista o
    que não pôde ser conferido (títulos ou passos que não correspondem ao
    inglês em quantidade e nível)."""
    problemas, n = [], 0
    te, tp = titulos(en), titulos(pt)
    linhas = pt.split('\n')
    if [lv for _, lv, _ in te] != [lv for _, lv, _ in tp]:
        problemas.append(f'títulos: en={len(te)} pt={len(tp)} (ou níveis diferentes)')
    else:
        for (_, _, txt_en), (i, nivel, txt_pt) in zip(te, tp):
            novo = com_id(txt_pt, slug(txt_en))
            if novo is not None:
                indent = linhas[i][:len(linhas[i]) - len(linhas[i].lstrip())]
                linhas[i] = f'{indent}{"#" * nivel} {novo}'
                n += 1
    pt = '\n'.join(linhas)

    pe, pp = passos(en), passos(pt)
    if len(pe) != len(pp):
        problemas.append(f'docs-step: en={len(pe)} pt={len(pp)}')
    else:
        partes, ult = [], 0
        for me, mp in zip(pe, pp):
            novo = com_id(mp.group(2), slug(me.group(2)))
            if novo is not None:
                partes += [pt[ult:mp.start(2)], novo]
                ult = mp.end(2)
                n += 1
        pt = ''.join(partes) + pt[ult:]
    return pt, n, problemas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='upstream/main')
    ap.add_argument('arquivos', nargs='+')
    a = ap.parse_args()
    for arq in a.arquivos:
        caminho = Path(arq).resolve().relative_to(ROOT).as_posix()
        en = subprocess.run(['git', '-C', str(ROOT), 'show', f'{a.ref}:{caminho}'],
                            capture_output=True, text=True, check=True).stdout
        pt = (ROOT / caminho).read_text(encoding='utf-8')
        novo, n, problemas = ancorar(en, pt)
        if n:
            (ROOT / caminho).write_text(novo, encoding='utf-8')
        for p in problemas:
            print(f'✗ {caminho}: {p}; ignorado')
        print(f'✓ {caminho}: {n} título(s) ajustado(s)')


if __name__ == '__main__':
    main()
