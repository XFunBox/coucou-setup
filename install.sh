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
    --help) echo 'Uso: bash install.sh [--dry-run | --configure-only]'; exit 0 ;;
    *) echo "Opción desconocida: $arg" >&2; exit 2 ;;
  esac
done
command -v python3 >/dev/null || { echo 'Se necesita Python 3.' >&2; exit 1; }
python3 "$ROOT/configure.py" --home "$TARGET_HOME" --check
if [[ "$MODE" == dry-run ]]; then
  echo 'Instalaría Coucou 0.3.0 amd64, localizaría/instalaría Codex y aplicaría settings.json y sus hooks.'
  echo 'Se conservarán otros hooks y las credenciales del llavero. Se crearán copias antes de escribir.'
  exit 0
fi
if [[ "$MODE" == install ]]; then
  [[ $(uname -m) == x86_64 ]] || { echo 'Este instalador admite Linux x86_64/amd64.' >&2; exit 1; }
  command -v apt-get >/dev/null || { echo 'Se necesita Ubuntu/Debian con apt-get.' >&2; exit 1; }
  [[ $EUID != 0 ]] || { echo 'Ejecuta como tu usuario: bash install.sh (solicitará sudo para apt).' >&2; exit 1; }
  command -v sudo >/dev/null
  sudo apt-get install -y curl ca-certificates python3
  TASK_TMP=$(mktemp -d)
  trap 'rm -rf -- "$TASK_TMP"' EXIT
  curl --fail --location --retry 3 'https://github.com/Louis-CFM/coucou/releases/download/linux-v0.3.0/Coucou-Linux-0.3.0-amd64.deb' -o "$TASK_TMP/coucou.deb"
  echo '296f27fb83260fa1975d3fcebfb0c2e01a6b9667750ca82dc8dd81ef81352bee  '"$TASK_TMP/coucou.deb" | sha256sum --check --status
  sudo apt-get install -y "$TASK_TMP/coucou.deb"
  if ! command -v codex >/dev/null && [[ ! -x "$TARGET_HOME/.local/bin/codex" ]] && [[ ! -x /usr/lib/chatgpt/resources/codex ]]; then
    curl --fail --location --retry 3 'https://github.com/openai/codex/releases/download/rust-v0.159.2/codex-x86_64-unknown-linux-musl.tar.gz' -o "$TASK_TMP/codex.tar.gz"
    echo '26586b0d246d41a799b0ef8ee1add370f0fb0721b3709340f28db612381616ea  '"$TASK_TMP/codex.tar.gz" | sha256sum --check --status
    tar -xzf "$TASK_TMP/codex.tar.gz" -C "$TASK_TMP" codex-x86_64-unknown-linux-musl
    mkdir -p "$TARGET_HOME/.local/bin"
    install -m 755 "$TASK_TMP/codex-x86_64-unknown-linux-musl" "$TARGET_HOME/.local/bin/codex"
  fi
fi
[[ -x /usr/bin/coucou && -x /usr/lib/Coucou/coucou-hook ]] || { echo 'Instala Coucou 0.3.0 antes de --configure-only.' >&2; exit 1; }
# Esperar al cierre antes de cambiar ajustes evita que la app sobrescriba el archivo.
if pgrep -u "$(id -u)" -x coucou >/dev/null; then
  pkill -TERM -u "$(id -u)" -x coucou
  for _ in {1..50}; do
    pgrep -u "$(id -u)" -x coucou >/dev/null || break
    sleep 0.1
  done
  if pgrep -u "$(id -u)" -x coucou >/dev/null; then
    echo 'Coucou sigue abierto. Ciérralo desde su icono y ejecuta bash install.sh --configure-only.' >&2; exit 1
  fi
fi
python3 "$ROOT/configure.py" --home "$TARGET_HOME" --relay /usr/lib/Coucou/coucou-hook
mkdir -p "$TARGET_HOME/.local/bin"
if [[ ! -e "$TARGET_HOME/.local/bin/codex" && ! -L "$TARGET_HOME/.local/bin/codex" ]] && [[ -x /usr/lib/chatgpt/resources/codex ]]; then
  ln -s /usr/lib/chatgpt/resources/codex "$TARGET_HOME/.local/bin/codex"
fi
if [[ -n ${DISPLAY:-}${WAYLAND_DISPLAY:-} ]]; then
  nohup /usr/bin/coucou >/dev/null 2>&1 &
  echo 'Coucou iniciado.'
else
  echo 'Coucou arrancará en el próximo inicio de sesión gráfico.'
fi
echo 'Configuración aplicada. En Codex: inicia sesión y revisa /hooks. En Coucou: añade tu token GitHub desde Settings → Integrations.'
