#!/usr/bin/env bash
# Cambia solo la imagen backend; conserva el entorno privado y valida Compose.
set -euo pipefail
readonly REPO_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
readonly TARGET=/etc/sentinel/backend.env
readonly IMAGE=${1:?Uso: sudo -n bash scripts/configure-backend-image.sh sentinel-backend:tag-inmutable}
[[ $EUID -eq 0 ]] || { echo 'Ejecutar mediante sudo -n.' >&2; exit 1; }
[[ $IMAGE == sentinel-backend:* && $IMAGE != sentinel-backend:latest ]] || { echo 'Se requiere imagen backend versionada.' >&2; exit 1; }
umask 077
readonly STAGED=$(mktemp /etc/sentinel/.backend-image.XXXXXX)
trap 'rm -f -- "$STAGED"' EXIT
seen=0
while IFS= read -r line || [[ -n $line ]]; do
    case $line in
        SENTINEL_BACKEND_IMAGE=*) printf 'SENTINEL_BACKEND_IMAGE=%s\n' "$IMAGE"; seen=$((seen + 1)) ;;
        *) printf '%s\n' "$line" ;;
    esac
done < "$TARGET" > "$STAGED"
[[ $seen -le 1 ]] || { echo 'Imagen duplicada; original preservado.' >&2; exit 1; }
[[ $seen -ne 0 ]] || printf 'SENTINEL_BACKEND_IMAGE=%s\n' "$IMAGE" >> "$STAGED"
docker compose --env-file "$STAGED" -f "$REPO_DIR/docker-compose.fenix.yml" config --quiet
readonly BACKUP="$TARGET.pre-backend-image-$(date -u +%Y%m%dT%H%M%SZ)"
cp -a -- "$TARGET" "$BACKUP"
chown root:docker "$STAGED"
chmod 0640 "$STAGED"
mv -f -- "$STAGED" "$TARGET"
printf 'Imagen backend configurada; backup: %s\n' "$BACKUP"
