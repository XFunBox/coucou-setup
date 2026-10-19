#!/usr/bin/env bash
set -euo pipefail
umask 077
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
TARGET_HOME=${HOME:?}
MODE=install
for arg in "$@"; do
  case "$arg" in
    --dry-run) MODE=dry-run ;;
    --configure-only) MODE=configure ;;
    --build-only) MODE=build ;;
    --help) echo 'Uso: bash install.sh [--dry-run | --configure-only | --build-only]'; exit 0 ;;
    *) echo "Opción desconocida: $arg" >&2; exit 2 ;;
  esac
done
[[ $# -le 1 ]] || { echo 'Usa una sola opción.' >&2; exit 2; }
command -v python3 >/dev/null || { echo 'Se necesita Python 3.' >&2; exit 1; }
python3 "$ROOT/configure.py" --home "$TARGET_HOME" --check
VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/source-lock.json")
if [[ "$MODE" == dry-run ]]; then
  echo "Compilaría Coucou $VERSION desde fuente oficial fijada y el parche local, usando Docker."
  echo 'Instalaría el binario personalizado, sus accesos, ajustes y diez hooks de Codex.'
  echo 'GitHub: repositorios, últimos commits y pipelines activos. Aprobaciones: clic explícito en la isla.'
  echo 'Se conservarán otros hooks y las credenciales del llavero; se crearán copias antes de escribir.'
  exit 0
fi
[[ $(uname -m) == x86_64 && $(uname -s) == Linux ]] || { echo 'Se necesita Linux x86_64/amd64.' >&2; exit 1; }
[[ $EUID != 0 ]] || { echo 'Ejecuta como tu usuario; se solicitará sudo solo para dependencias/Docker.' >&2; exit 1; }
RELEASE="$ROOT/.build/release"
if [[ "$MODE" == install || "$MODE" == build ]]; then
  command -v apt-get >/dev/null || { echo 'Se necesita Ubuntu/Debian con apt-get.' >&2; exit 1; }
  command -v sudo >/dev/null
  sudo apt-get update
  PACKAGES=(curl ca-certificates git python3)
  command -v docker >/dev/null || PACKAGES+=(docker.io)
  if [[ "$MODE" == install ]]; then
    PACKAGES+=(libwebkit2gtk-4.1-0 libgtk-layer-shell0 libayatana-appindicator3-1 librsvg2-2)
  fi
  sudo apt-get install -y "${PACKAGES[@]}"
  bash "$ROOT/build.sh"
fi
# Comprobar versión, fuente/parche y hashes antes de detener la app o escribir.
python3 - "$ROOT" "$RELEASE" <<'PY'
import hashlib, json, sys
from pathlib import Path
root, release = map(Path, sys.argv[1:])
lock = json.loads((root/'source-lock.json').read_text())
assert (release/'VERSION').read_text().strip() == lock['version'], 'La versión compilada no coincide'
assert json.loads((release/'source-lock.json').read_text()) == lock, 'La compilación corresponde a otro parche/fuente'
assert hashlib.sha256((root/'patches/sendoa.patch').read_bytes()).hexdigest() == lock['patchSha256'], 'El parche ha cambiado'
assert hashlib.sha256((root/'patches/desktop.patch').read_bytes()).hexdigest() == lock['desktopPatchSha256'], 'El parche de escritorio ha cambiado'
seen = set()
for line in (release/'SHA256SUMS').read_text().splitlines():
    checksum, name = line.split()
    assert name in {'coucou','coucou-hook','codex-bridge.mjs'} and name not in seen, 'Nombre inesperado o duplicado en las sumas'
    seen.add(name)
    assert hashlib.sha256((release/name).read_bytes()).hexdigest() == checksum, 'Binario modificado: '+name
assert seen == {'coucou','coucou-hook','codex-bridge.mjs'}, 'Faltan sumas de los binarios y del puente'
PY
if [[ "$MODE" == build ]]; then echo 'Compilación comprobada; no se aplicó configuración.'; exit 0; fi
mkdir -p "$TARGET_HOME/.local/bin"
if ! command -v codex >/dev/null && [[ ! -e "$TARGET_HOME/.local/bin/codex" && ! -L "$TARGET_HOME/.local/bin/codex" ]]; then
  if [[ -x /usr/lib/chatgpt/resources/codex ]]; then
    ln -s /usr/lib/chatgpt/resources/codex "$TARGET_HOME/.local/bin/codex"
  else
    if [[ "$MODE" == configure ]]; then
      echo 'No se encuentra Codex; ejecuta la instalación completa o instala Codex antes.' >&2; exit 1
    fi
    TASK_TMP=$(mktemp -d)
    trap 'rm -rf -- "$TASK_TMP"' EXIT
    curl --fail --location --retry 3 'https://github.com/openai/codex/releases/download/rust-v0.159.2/codex-x86_64-unknown-linux-musl.tar.gz' -o "$TASK_TMP/codex.tar.gz"
    echo "26586b0d246d41a799b0ef8ee1add370f0fb0721b3709340f28db612381616ea  $TASK_TMP/codex.tar.gz" | sha256sum --check --status
    tar -xzf "$TASK_TMP/codex.tar.gz" -C "$TASK_TMP" codex-x86_64-unknown-linux-musl
    install -m 755 "$TASK_TMP/codex-x86_64-unknown-linux-musl" "$TARGET_HOME/.local/bin/codex"
  fi
fi
if pgrep -u "$(id -u)" -x coucou >/dev/null; then
  pkill -TERM -u "$(id -u)" -x coucou
  for _ in {1..50}; do
    pgrep -u "$(id -u)" -x coucou >/dev/null || break
    sleep 0.1
  done
  if pgrep -u "$(id -u)" -x coucou >/dev/null; then
    echo 'Cierra Coucou desde su icono y vuelve a ejecutar --configure-only.' >&2; exit 1
  fi
fi
python3 "$ROOT/configure.py" --home "$TARGET_HOME" --relay "$RELEASE/coucou-hook" --binary "$RELEASE/coucou" --bridge "$RELEASE/codex-bridge.mjs"
if [[ -n ${DISPLAY:-}${WAYLAND_DISPLAY:-} ]]; then
  nohup "$TARGET_HOME/.local/share/coucou-local/bin/coucou" >/dev/null 2>&1 &
  echo "Coucou $VERSION iniciado."
else
  echo 'Coucou arrancará en el próximo inicio de sesión gráfico.'
fi
echo 'En Codex: inicia sesión y revisa /hooks; selecciona Pedir aprobación para recibir solicitudes en la isla.'
echo 'En Coucou: configura GitHub con lectura de Contents, Actions, Commit statuses, Pull requests y Metadata.'
