#!/usr/bin/env bash
# Gera o indice da busca pra funcionar no "hugo server".
#
# O Pagefind indexa HTML pronto, e "hugo server" serve da memoria, sem escrever
# em public/. Entao o caminho e: buildar de verdade, indexar o resultado e
# copiar o indice pra static/, que o dev server serve em /pagefind/.
#
# Uso:  ./bin/indexar-busca.sh   e depois   hugo server
#
# O indice fica desatualizado conforme voce edita: rode de novo quando quiser
# buscar em conteudo novo. static/pagefind/ e ignorado pelo git.
set -euo pipefail

VERSAO="1.5.2"                    # mesma do workflow, pra nao divergir
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/pagefind"
BIN="$CACHE/pagefind-$VERSAO"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -x "$BIN" ]; then
  echo "==> baixando pagefind $VERSAO"
  mkdir -p "$CACHE"
  tmp="$(mktemp -d)"
  arq="pagefind-v$VERSAO-x86_64-unknown-linux-musl.tar.gz"
  curl -sSfL -o "$tmp/$arq" \
    "https://github.com/CloudCannon/pagefind/releases/download/v$VERSAO/$arq"
  tar -xzf "$tmp/$arq" -C "$tmp"
  mv "$tmp/pagefind" "$BIN"
  chmod +x "$BIN"
  rm -rf "$tmp"
fi

saida="$(mktemp -d)"
trap 'rm -rf "$saida"' EXIT

echo "==> hugo build"
( cd "$RAIZ" && hugo --quiet --destination "$saida" )

echo "==> pagefind"
"$BIN" --site "$saida"

echo "==> copiando indice pra static/pagefind"
rm -rf "$RAIZ/static/pagefind"
cp -r "$saida/pagefind" "$RAIZ/static/pagefind"

echo
echo "pronto. agora: hugo server"
