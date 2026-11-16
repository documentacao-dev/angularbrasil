#!/usr/bin/env bash
# Prepara um ambiente do zero (sessão nova na nuvem, CI) para o ciclo de
# tradução: configura o remote `upstream` (angular/angular) e busca o
# histórico necessário SEM baixar o repositório inteiro.
#
#   bash tool/traducao/setup.sh
#
# O angular/angular tem gigabytes de histórico. O fetch é parcial
# (--filter=blob:none: só commits e árvores) e, em clone raso (CI), também
# raso (--depth); os blobs de
# adev/src/content/ são baixados de uma vez no fim. Não instala pnpm/Bazel:
# o ciclo de tradução só precisa de git e python3. O build do site roda no
# workflow firebase-deploy.yml.
set -euo pipefail
cd "$(dirname "$0")/../.."

PROFUNDIDADE=${PROFUNDIDADE:-3000}

if ! git remote get-url upstream >/dev/null 2>&1; then
  git remote add upstream https://github.com/angular/angular.git
fi
# Num clone completo do fork o histórico do upstream já está quase todo aqui:
# um fetch sem --depth só traz os commits novos. NUNCA use --depth num clone
# completo: ele torna o repositório inteiro raso (.git/shallow).
if [ "$(git rev-parse --is-shallow-repository)" = true ]; then
  git fetch -q --filter=blob:none --depth="$PROFUNDIDADE" upstream main
else
  git fetch -q --filter=blob:none upstream main
fi

base=$(cat tool/traducao/ultimo-sync-upstream.txt)
if ! git cat-file -e "$base^{commit}" 2>/dev/null; then
  echo "Commit do último sync ($base) fora das $PROFUNDIDADE versões buscadas."
  echo "Rode de novo com PROFUNDIDADE maior, ex.: PROFUNDIDADE=10000 bash $0"
  exit 1
fi

# Blobs do conteúdo de docs no último sync e no upstream atual, de uma vez só.
vazio=4b825dc642cb6eb9a060e54bf8d69288fbee4904
git diff --stat "$vazio" "$base" -- adev/src/content/ >/dev/null
git diff --stat "$base" upstream/main -- adev/src/content/ >/dev/null

python3 -c 'import sys; assert sys.version_info >= (3, 8)' \
  || { echo "Precisa de python3 >= 3.8"; exit 1; }
echo "Pronto. upstream/main = $(git rev-parse --short upstream/main);" \
  "commits em adev/src/content desde o último sync:" \
  "$(git rev-list --count "$base"..upstream/main -- adev/src/content)"
