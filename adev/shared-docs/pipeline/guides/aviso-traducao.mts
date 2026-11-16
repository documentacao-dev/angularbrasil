/*!
 * @license
 * Copyright Google LLC All Rights Reserved.
 *
 * Use of this source code is governed by an MIT-style license that can be
 * found in the LICENSE file at https://angular.dev/license
 */

// Angular Brasil: aviso de página ainda não traduzida.
//
// Uma página de adev/src/content/ conta como traduzida quando começa com
// `<!-- ia-translate: true -->` (a mesma regra de tool/traducao/). Nas que
// não começam, o build insere no topo do conteúdo, logo depois do título, um
// aviso em português com o link para o .md da página no fork. A decisão é
// tomada aqui, na geração do HTML, e não no navegador.

/** Marcador de página traduzida (primeira linha do .md). */
export const MARCADOR_TRADUZIDA = '<!-- ia-translate: true -->';

const PASTA_CONTEUDO = 'adev/src/content/';
const URL_FONTE_NO_FORK = 'https://github.com/documentacao-dev/angularbrasil/blob/main/';

/**
 * Pastas de adev/src/content/ que não são páginas de documentação (o README
 * vira texto de outra interface, como o playground e a home dos tutoriais).
 */
const FORA_DA_DOCUMENTACAO = ['tutorials/homepage/', 'tutorials/playground/'];

/**
 * Caminho do .md a partir de `adev/src/content/` (ex.: `guide/signals.md`),
 * ou `null` se o arquivo não for uma página de documentação.
 */
export function caminhoNoConteudo(filePath: string): string | null {
  const normalizado = filePath.replace(/\\/g, '/');
  const i = normalizado.lastIndexOf(PASTA_CONTEUDO);
  if (i === -1) {
    return null;
  }
  const relativo = normalizado.slice(i + PASTA_CONTEUDO.length);
  if (
    !relativo.endsWith('.md') ||
    relativo.includes('node_modules/') ||
    FORA_DA_DOCUMENTACAO.some((pasta) => relativo.startsWith(pasta))
  ) {
    return null;
  }
  return relativo;
}

/** Se o conteúdo Markdown está marcado como traduzido. */
export function estaTraduzida(markdown: string): boolean {
  return markdown.trimStart().startsWith(MARCADOR_TRADUZIDA);
}

/** HTML do aviso para a página `relativo` (caminho dentro de adev/src/content/). */
export function htmlDoAviso(relativo: string): string {
  const href = URL_FONTE_NO_FORK + PASTA_CONTEUDO + relativo;
  return `
  <aside class="docs-callout docs-callout-important docs-aviso-traducao" lang="pt-BR" aria-label="Aviso de tradução">
    <p>
      <strong>Esta página ainda está em inglês.</strong>
      A tradução para o português ainda não chegou aqui. Quer ajudar?
      <a href="${href}" target="_blank" rel="noopener">Traduza no GitHub<span class="docs-aviso-traducao-seta" aria-hidden="true"> →</span><span class="docs-aviso-traducao-sr"> (abre em nova aba)</span></a>
    </p>
  </aside>
  `;
}

/**
 * Índice logo depois do `</div>` que fecha o `<div>` aberto em `inicio`
 * (conta os `<div>` aninhados), ou -1.
 */
function fimDoDiv(html: string, inicio: number): number {
  const tag = /<div\b|<\/div>/g;
  tag.lastIndex = inicio;
  let profundidade = 0;
  for (let m = tag.exec(html); m !== null; m = tag.exec(html)) {
    profundidade += m[0] === '</div>' ? -1 : 1;
    if (profundidade === 0) {
      return m.index + m[0].length;
    }
  }
  return -1;
}

/** Índice logo depois do cabeçalho da página (título), ou 0 se não houver. */
function fimDoCabecalho(html: string): number {
  const header = html.indexOf('<header class="docs-header">');
  const decorativo = html.indexOf('<div class="docs-decorative-header-container">');
  if (header !== -1 && (decorativo === -1 || header < decorativo)) {
    const fim = html.indexOf('</header>', header);
    return fim === -1 ? 0 : fim + '</header>'.length;
  }
  if (decorativo !== -1) {
    return Math.max(fimDoDiv(html, decorativo), 0);
  }
  return 0;
}

/**
 * Devolve o HTML da página com o aviso inserido logo depois do cabeçalho
 * (`<header class="docs-header">` do título `#`, ou o
 * `<docs-decorative-header>`) ou, se não houver cabeçalho, no começo.
 * Páginas traduzidas e arquivos fora da documentação voltam sem mudança.
 */
export function inserirAvisoDeTraducao(html: string, markdown: string, filePath: string): string {
  const relativo = caminhoNoConteudo(filePath);
  if (relativo === null || estaTraduzida(markdown)) {
    return html;
  }
  const corte = fimDoCabecalho(html);
  return html.slice(0, corte) + htmlDoAviso(relativo) + html.slice(corte);
}
