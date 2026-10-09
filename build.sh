#!/usr/bin/env bash
set -euo pipefail
umask 077
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
MODE=build
case "${1:-}" in
  '') ;;
  --prepare-only) MODE=prepare ;;
  --help) echo 'Uso: bash build.sh [--prepare-only]'; exit 0 ;;
  *) echo 'Opción de compilación desconocida.' >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || { echo 'Demasiadas opciones.' >&2; exit 2; }
command -v python3 >/dev/null
command -v curl >/dev/null
command -v git >/dev/null
[[ $(uname -m) == x86_64 && $(uname -s) == Linux ]] || { echo 'Se necesita Linux x86_64.' >&2; exit 1; }
python3 - "$ROOT" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); lock = json.loads((root/'source-lock.json').read_text())
assert hashlib.sha256((root/'patches/sendoa.patch').read_bytes()).hexdigest() == lock['patchSha256'], 'El parche no coincide con source-lock.json'
PY
SOURCE_URL=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sourceUrl"])' "$ROOT/source-lock.json")
SOURCE_SHA=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sourceSha256"])' "$ROOT/source-lock.json")
VERSION=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$ROOT/source-lock.json")
NODE_IMAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["nodeImage"])' "$ROOT/source-lock.json")
RUST_IMAGE=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["rustImage"])' "$ROOT/source-lock.json")
mkdir -p "$ROOT/.build"
TASK_TMP=$(mktemp -d "$ROOT/.build/source.XXXXXXXX")
EXPORT_TMP=
TASK_CONTAINER=
cleanup() {
  if [[ -n "$TASK_CONTAINER" ]]; then "${DOCKER[@]}" rm "$TASK_CONTAINER" >/dev/null 2>&1 || true; fi
  rm -rf -- "$TASK_TMP"
  if [[ -n "$EXPORT_TMP" ]]; then rm -rf -- "$EXPORT_TMP"; fi
}
trap cleanup EXIT
curl --fail --location --retry 3 "$SOURCE_URL" -o "$TASK_TMP/source.tar.gz"
echo "$SOURCE_SHA  $TASK_TMP/source.tar.gz" | sha256sum --check --status
mkdir "$TASK_TMP/context"
tar -xzf "$TASK_TMP/source.tar.gz" --strip-components=1 -C "$TASK_TMP/context"
# Aislar el árbol: sin esto Git podría encontrar el .git del setup padre e
# ignorar rutas del parche por ejecutarse en un subdirectorio del repositorio.
git -C "$TASK_TMP/context" init --quiet
git -C "$TASK_TMP/context" apply --check "$ROOT/patches/sendoa.patch"
git -C "$TASK_TMP/context" apply "$ROOT/patches/sendoa.patch"
cp "$ROOT/Dockerfile" "$TASK_TMP/context/Dockerfile"
printf '.git\n**/node_modules\n**/target\n**/dist\n' > "$TASK_TMP/context/.dockerignore"
if [[ "$MODE" == prepare ]]; then
  DEST="$ROOT/.build/source-$VERSION"
  [[ ! -e "$DEST" ]] || { echo "Ya existe $DEST; usa otra copia del repo para repetir." >&2; exit 1; }
  mv "$TASK_TMP/context" "$DEST"
  echo "Fuente verificada y parche aplicado: $DEST"
  exit 0
fi
DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  command -v sudo >/dev/null || { echo 'No hay acceso a Docker.' >&2; exit 1; }
  DOCKER=(sudo docker)
  "${DOCKER[@]}" info >/dev/null
fi
IMAGE="coucou-setup-local:$VERSION"
"${DOCKER[@]}" build --build-arg "NODE_IMAGE=$NODE_IMAGE" --build-arg "RUST_IMAGE=$RUST_IMAGE" \
  -t "$IMAGE" "$TASK_TMP/context"
EXPORT_TMP=$(mktemp -d "$ROOT/.build/export.XXXXXXXX")
TASK_CONTAINER=$("${DOCKER[@]}" create "$IMAGE" /coucou)
for file in coucou coucou-hook LICENSE LICENSE-ASSETS.md SHA256SUMS; do
  "${DOCKER[@]}" cp "$TASK_CONTAINER:/$file" "$EXPORT_TMP/$file"
done
"${DOCKER[@]}" rm "$TASK_CONTAINER" >/dev/null
TASK_CONTAINER=
(cd "$EXPORT_TMP" && sha256sum --check SHA256SUMS)
printf '%s\n' "$VERSION" > "$EXPORT_TMP/VERSION"
python3 - "$ROOT" "$EXPORT_TMP" <<'PY'
import json, shutil, sys
from pathlib import Path
root, export = map(Path, sys.argv[1:])
shutil.copy2(root/'source-lock.json', export/'source-lock.json')
PY
rm -rf -- "$ROOT/.build/release"
mv "$EXPORT_TMP" "$ROOT/.build/release"
EXPORT_TMP=
echo "Compilación lista: $ROOT/.build/release ($VERSION)"
