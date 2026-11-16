#!/usr/bin/env python3
"""Checagens determinísticas das traduções do Angular Brasil.

    python3 tool/traducao/verificar.py [--ref upstream/main] [--estrito] [arquivos...]

Sem arquivos, confere todas as páginas de adev/src/content/ marcadas com
`<!-- ia-translate: true -->` (e as checagens globais). Erros fazem o script
sair com código 1; avisos só são listados, a menos que se passe --estrito.

O original em inglês de cada página é `git show <ref>:<caminho>` (o fork não
guarda cópia `.en.md`).

Checagens:

ERROS
- conflito:     marcadores de merge (<<<<<<<, |||||||, >>>>>>>) no arquivo.
- flag:         `<!-- ia-translate: true -->` ausente ou fora da primeira linha.
- placeholder:  avisos de "tradução pendente" deixados no texto.
- ingles:       página marcada como traduzida cuja prosa está em inglês
                (proporção de palavras-função em inglês >= 0.7).
- estrutura:    número de cercas ```, de cada tag <docs-*> (docs-code,
                docs-callout, docs-step, docs-card, docs-tab...) ou de âncoras
                {#id} diferente do inglês; títulos que não correspondem ao
                inglês em quantidade e nível.
- tags:         tag pareada aberta sem fechar (<docs-callout>, <docs-step>,
                <docs-card>, <docs-tab>, <docs-workflow>...). É a mesma regra de
                adev/shared-docs/pipeline/shared/marked/validate-paired-tags.mts,
                que derruba o build.
- atributos:    valor de atributo que não é texto (path, region, href, link,
                language, preview, visibleLines, src...) diferente do inglês
                nas tags <docs-*>. Só `title`, `header`, `label`,
                `description`, `headerTitle` e `link` (o texto do botão do
                <docs-card>; o destino fica em `href`) são traduzíveis.
- alerta:       prefixos de alerta (NOTE:, TIP:, IMPORTANT:, CRITICAL:,
                HELPFUL:, QUESTION:, SUMMARY:, TLDR:, TODO:) em quantidade
                diferente do inglês ou traduzidos (NOTA:, DICA:...). O
                renderizador só reconhece os prefixos em inglês.
- link:         destino de link (`](url)`, `href="..."`, `[x]: url`) que existe
                só no português ou só no inglês (o MDN em pt-BR no lugar do
                en-US é aceito).
- ancora:       título ou título de <docs-step> traduzido sem `{#id}` com o id
                do inglês (links #ancora quebrariam). Corrija com
                tool/traducao/ancorar_titulos.py <arquivo>.
- id-duplicado: dois títulos com o mesmo id (o build do adev recusa).
- link-interno: link para âncora da própria página que não existe.
- defasada:     o inglês da página mudou no upstream desde o último sync
                (tool/traducao/ultimo-sync-upstream.txt): rode
                sincronizar_upstream.py.
- pendente:     .traducao-pendente/ ainda tem arquivos para resolver.
- workflow:     workflow do ciclo ausente, ou com `if: github.repository`
                que não inclui documentacao-dev/angularbrasil.
- analytics:    Google Analytics ou banner de cookies do angular.dev de volta em
                adev/ (fora de src/content/ e node_modules/): G-XB6NEVW32B,
                googleAnalyticsId, gtag, googletagmanager, cookie-popup,
                setCookieConsent. O fork removeu (PR #69); um sync que traga
                código do site (--escopo adev/src/app/ etc.) deve removê-los
                de novo.

AVISOS
- parcial:      proporção de inglês entre 0.3 e 0.7 (tradução incompleta).
- orfa:         arquivo marcado que não existe no upstream (restos de
                traduções antigas, como as pastas `pt-br/`). Não é publicado
                com conteúdo do upstream; apague ou mova para o caminho certo.
"""
import argparse
import importlib.util
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTENT = 'adev/src/content/'
SYNC = ROOT / 'tool' / 'traducao' / 'ultimo-sync-upstream.txt'
PEND = ROOT / '.traducao-pendente'
REPO_FORK = 'documentacao-dev/angularbrasil'
WORKFLOWS_DO_CICLO = ('firebase-deploy.yml', 'traducao-automatica.yml')
VAZIO = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'  # árvore vazia do git

FLAG = '<!-- ia-translate: true -->'
CONFLITO = re.compile(r'^(<{7} |\|{7} |>{7} )', re.M)
PLACEHOLDER = re.compile(
    r'note for translators|to be translated|marked for translation'
    r'|tradu[çc][ãa]o pendente|todo:? traduzir', re.I)
TAG_DOCS = re.compile(r'<(docs-[a-z-]+)(?=[\s>/])')
ANCORAS = re.compile(r'\{#\s*[\w-]+\s*\}')
PAREADAS = ('docs-callout', 'docs-card', 'docs-card-container',
            'docs-decorative-header', 'docs-step', 'docs-tab', 'docs-tab-group',
            'docs-workflow')
ABERTURA_DOCS = re.compile(r'<docs-[a-z-]+\b[^>]*>', re.S)
ATRIBUTO = re.compile(r'\b([a-zA-Z][\w-]*)\s*=\s*"([^"]*)"')
ATRIBUTOS_TEXTO = {'title', 'header', 'label', 'description', 'link', 'headerTitle'}
ALERTAS = ('NOTE', 'TIP', 'TODO', 'QUESTION', 'SUMMARY', 'TLDR', 'CRITICAL',
           'IMPORTANT', 'HELPFUL')
ALERTA = re.compile(rf'^\s*({"|".join(ALERTAS)}): ', re.M)
ALERTA_TRADUZIDO = re.compile(
    r'^\s*(NOTA|OBSERVAÇÃO|DICA|IMPORTANTE|CRÍTICO|ÚTIL|PERGUNTA|RESUMO'
    r'|ATENÇÃO|AVISO|FAZER): ', re.M)
LINK_MD = re.compile(r'\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
LINK_HREF = re.compile(r'\bhref="([^"]+)"')
LINK_DEF = re.compile(r'^\s*\[[^\]]+\]:\s*(\S+)', re.M)

# Palavras-função para estimar o idioma da prosa.
EN = set('the and of to is are you your this that with for in it be can when '
         'which by an or as from have will not these use using'.split())
PT = set('os de do da dos das que é são um uma para com no na nos nas em por '
         'você seu sua ao como mais pode isso este esta'.split())
LIMITE_ERRO, LIMITE_AVISO, MINIMO_PALAVRAS = 0.7, 0.3, 20

ANC = None  # módulo ancorar_titulos.py


def git(*args):
    r = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def prebuscar(*refs):
    """Num clone parcial (--filter=blob:none) cada `git show` baixaria um blob
    por vez. Um diff contra a árvore vazia baixa todos os de CONTENT de uma
    vez só."""
    for ref in refs:
        if ref:
            subprocess.run(['git', '-C', str(ROOT), 'diff', '--stat', VAZIO, ref,
                            '--', CONTENT], capture_output=True)


def sem_codigo(texto):
    texto = re.sub(r'```.*?```', '', texto, flags=re.S)
    return re.sub(r'<docs-code\b[^>]*>.*?</docs-code>', '', texto, flags=re.S)


def proporcao_ingles(texto):
    corpo = re.sub(r'<!--.*?-->|<[^<>]*>', ' ', sem_codigo(texto), flags=re.S)
    linhas = []
    for linha in corpo.split('\n'):
        s = linha.strip()
        if not s or s.startswith(('<', '[', '|')):
            continue
        linhas.append(re.sub(r'`[^`]*`|\[[^\]]*\]\([^)]*\)|\{[^}]*\}', '', s))
    palavras = re.findall(r"[a-záéíóúãõçêâô']+", ' '.join(linhas).lower())
    e = sum(p in EN for p in palavras)
    p = sum(p in PT for p in palavras)
    return (e / (e + p), e + p) if e + p else (0.0, 0)


def tags_desbalanceadas(texto):
    t = re.sub(r'```[\s\S]*?```|<!--[\s\S]*?-->|`[^`\n]*`', '', texto)
    res = []
    for tag in PAREADAS:
        ab = len(re.findall(rf'<{tag}(?=[\s>])(?![^>]*/>)', t))
        fe = len(re.findall(rf'</{tag}>', t))
        if ab != fe:
            res.append(f'<{tag}> {ab} aberta(s), {fe} fechada(s)')
    return res


def atributos(texto):
    c = Counter()
    for tag in ABERTURA_DOCS.findall(re.sub(r'```.*?```', '', texto, flags=re.S)):
        for nome, valor in ATRIBUTO.findall(tag):
            if nome not in ATRIBUTOS_TEXTO:
                c[f'{nome}="{valor}"'] += 1
    return c


def links(texto):
    t = re.sub(r'```.*?```', '', texto, flags=re.S)
    # O MDN em português é uma troca aceita: compara como se fosse o en-US.
    t = t.replace('developer.mozilla.org/pt-BR/', 'developer.mozilla.org/en-US/')
    return set(LINK_MD.findall(t)) | set(LINK_HREF.findall(t)) | set(LINK_DEF.findall(t))


def ids_da_pagina(texto):
    ids = set(re.findall(r'\bid="([^"]+)"', texto))
    ids.update(ANC.slug(t) for _, _, t in ANC.titulos(texto))
    ids.update(ANC.slug(m.group(2)) for m in ANC.passos(texto))
    return ids


def ids_duplicados(texto):
    ids = [ANC.slug(t) for _, _, t in ANC.titulos(texto)]
    ids += [ANC.slug(m.group(2)) for m in ANC.passos(texto)]
    return {i for i, n in Counter(ids).items() if n > 1}


def links_internos_quebrados(texto):
    t = sem_codigo(texto)
    alvos = re.findall(r'\]\(#([^)\s]+)\)', t) + re.findall(r'href="#([^"]+)"', t)
    ids = ids_da_pagina(texto)
    return {a for a in alvos if a not in ids}


def checar_arquivo(caminho, ref, sync):
    erros, avisos = [], []
    texto = (ROOT / caminho).read_text(encoding='utf-8')

    if CONFLITO.search(texto):
        erros.append(('conflito', 'marcadores de merge no arquivo'))
    if not texto.startswith(FLAG):
        onde = 'fora da primeira linha' if FLAG in texto else 'ausente'
        erros.append(('flag', f'`{FLAG}` {onde}'))
    for linha in texto.split('\n'):
        if PLACEHOLDER.search(linha):
            erros.append(('placeholder', linha.strip()[:90]))
            break

    en = git('show', f'{ref}:{caminho}')
    if en is None:
        avisos.append(('orfa', f'não existe em {ref[:9]}'))
        return erros, avisos

    prop, n = proporcao_ingles(texto)
    if n >= MINIMO_PALAVRAS and prop >= LIMITE_ERRO:
        erros.append(('ingles', f'marcada como traduzida, mas {prop:.0%} da prosa está em inglês'))
    elif n >= MINIMO_PALAVRAS and prop >= LIMITE_AVISO:
        avisos.append(('parcial', f'{prop:.0%} da prosa ainda em inglês'))

    # Estrutura
    ne, np_ = len(re.findall(r'^\s*```', en, re.M)), len(re.findall(r'^\s*```', texto, re.M))
    if ne != np_:
        erros.append(('estrutura', f'cercas ```: en={ne} pt={np_}'))
    ce, cp = Counter(TAG_DOCS.findall(en)), Counter(TAG_DOCS.findall(texto))
    for tag in sorted(set(ce) | set(cp)):
        if ce[tag] != cp[tag]:
            erros.append(('estrutura', f'<{tag}>: en={ce[tag]} pt={cp[tag]}'))
    ne, np_ = len(ANCORAS.findall(en)), len(ANCORAS.findall(texto))
    if np_ < ne:  # a mais é normal: títulos traduzidos levam o id em inglês
        erros.append(('estrutura', f'âncoras {{#id}}: en={ne} pt={np_}'))

    for msg in sorted(set(tags_desbalanceadas(texto)) - set(tags_desbalanceadas(en))):
        erros.append(('tags', msg))

    ae, ap = atributos(en), atributos(texto)
    if ae != ap:
        so_pt = sorted((ap - ae).elements())[:4]
        so_en = sorted((ae - ap).elements())[:4]
        erros.append(('atributos', f'só no pt: {so_pt}; só no en: {so_en}'))

    ne, np_ = len(ALERTA.findall(sem_codigo(en))), len(ALERTA.findall(sem_codigo(texto)))
    if ne != np_:
        erros.append(('alerta', f'prefixos NOTE:/TIP:/...: en={ne} pt={np_}'))
    trad = ALERTA_TRADUZIDO.findall(sem_codigo(texto))
    if trad:
        erros.append(('alerta', f'prefixo traduzido ({", ".join(sorted(set(trad)))}:); '
                                'mantenha NOTE:, TIP:, IMPORTANT: etc.'))

    # Destino que aparece no texto do outro idioma com outra marcação (ex.: um
    # link quebrado do upstream que a tradução consertou) não conta.
    le, lp = links(en), links(texto)
    so_pt = sorted(u for u in lp - le if u not in en)
    so_en = sorted(u for u in le - lp if u not in texto)
    if so_pt:
        erros.append(('link', 'só no pt: ' + ', '.join(so_pt[:5])))
    if so_en:
        erros.append(('link', 'só no en: ' + ', '.join(so_en[:5])))

    novo, n_anc, problemas = ANC.ancorar(en, texto)
    for p in problemas:
        erros.append(('estrutura', p))
    if n_anc:
        erros.append(('ancora', f'{n_anc} título(s) sem `{{#id}}` do inglês; '
                                'rode tool/traducao/ancorar_titulos.py'))
    dup = ids_duplicados(texto) - ids_duplicados(en)
    if dup:
        erros.append(('id-duplicado', ', '.join(sorted(dup))))
    quebrados = links_internos_quebrados(texto) - links_internos_quebrados(en)
    if quebrados:
        erros.append(('link-interno', 'âncoras inexistentes: ' + ', '.join(sorted(quebrados))))

    if sync and sync != ref:
        en_sync = git('show', f'{sync}:{caminho}')
        if en_sync is not None and en_sync != en:
            erros.append(('defasada', f'o inglês mudou entre {sync[:9]} e {ref[:9]}; '
                                      'rode sincronizar_upstream.py'))
    return erros, avisos


def marcados():
    saida = git('grep', '-lF', FLAG, '--', CONTENT) or ''
    return [p for p in saida.split() if p.endswith('.md')]


# Analytics do angular.dev que o fork removeu (PR #69): visitante daqui não
# pode virar dado na conta do Google/Angular.
ANALYTICS_UPSTREAM = ('G-XB6NEVW32B', 'googleAnalyticsId', 'gtag', 'googletagmanager',
                      'cookie-popup', 'setCookieConsent')


def analytics_do_upstream():
    """Linhas `arquivo:linha` de adev/ (fora de src/content e node_modules)
    com algum termo de ANALYTICS_UPSTREAM."""
    args = ['grep', '-nIF']
    for termo in ANALYTICS_UPSTREAM:
        args += ['-e', termo]
    saida = git(*args, '--', 'adev/', ':!adev/src/content/', ':!**/node_modules/**') or ''
    return [l for l in saida.splitlines() if l.strip()]


def problemas_de_workflow():
    res = []
    pasta = ROOT / '.github' / 'workflows'
    for nome in WORKFLOWS_DO_CICLO:
        wf = pasta / nome
        if not wf.exists():
            res.append(f'{nome} não existe')
            continue
        for cond in re.findall(r'^\s*if:.*github\.repository.*$', wf.read_text(), re.M):
            if REPO_FORK not in cond:
                res.append(f'{nome}: `{cond.strip()}` não deixa rodar em {REPO_FORK}')
    return res


def main():
    global ANC
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='upstream/main')
    ap.add_argument('--estrito', action='store_true', help='avisos também falham')
    ap.add_argument('arquivos', nargs='*')
    a = ap.parse_args()

    ref = git('rev-parse', a.ref)
    if ref is None:
        sys.exit(f'Ref {a.ref} não encontrada. Rode: bash tool/traducao/setup.sh')
    ref = ref.strip()
    sync = SYNC.read_text().strip() if SYNC.exists() else None
    if sync and git('cat-file', '-e', sync + '^{commit}') is None:
        sync = None  # histórico raso: pula a checagem de defasagem
    spec = importlib.util.spec_from_file_location(
        'anc', ROOT / 'tool' / 'traducao' / 'ancorar_titulos.py')
    ANC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ANC)
    prebuscar(ref, sync if sync != ref else None)

    arquivos = a.arquivos or marcados()
    total_erros = total_avisos = 0
    for arq in arquivos:
        p = Path(arq)
        caminho = p.resolve().relative_to(ROOT).as_posix() if p.exists() else arq
        erros, avisos = checar_arquivo(caminho, ref, sync)
        if erros or avisos:
            print(f'{"✗" if erros else "!"} {caminho}')
            for tipo, msg in erros:
                print(f'    erro  [{tipo}] {msg}')
            for tipo, msg in avisos:
                print(f'    aviso [{tipo}] {msg}')
        total_erros += bool(erros)
        total_avisos += bool(avisos) and not erros

    if not a.arquivos:
        if PEND.exists() and any(f.name != 'RELATORIO.md'
                                 for f in PEND.rglob('*') if f.is_file()):
            print('✗ .traducao-pendente/\n    erro  [pendente] ainda há conflitos para resolver')
            total_erros += 1
        wf = problemas_de_workflow()
        if wf:
            print('✗ .github/workflows/')
            for msg in wf:
                print(f'    erro  [workflow] {msg}')
            total_erros += 1
        achados = analytics_do_upstream()
        if achados:
            print('✗ adev/ (analytics do upstream)')
            for l in achados[:20]:
                print(f'    erro  [analytics] {l[:140]}')
            print('    É o Google Analytics/banner de cookies do angular.dev, que voltou '
                  'pelo upstream: remova no sync (ver CLAUDE.md, regra do sync).')
            total_erros += 1

    print(f'{len(arquivos)} arquivo(s) conferido(s): {total_erros} com erro, '
          f'{total_avisos} só com aviso.')
    sys.exit(1 if total_erros or (a.estrito and total_avisos) else 0)


if __name__ == '__main__':
    main()
