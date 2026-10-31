#!/usr/bin/env bash
# Actualiza solo la imagen Cortex y su URL MyCNet, sin imprimir el entorno privado.
set -euo pipefail
readonly REPO_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
readonly TARGET=/etc/sentinel/backend.env
readonly IMAGE=${1:?Uso: sudo -n bash scripts/configure-cortex-uplink.sh sentinel-cortex:tag-inmutable}
[[ $EUID -eq 0 ]] || { echo 'Ejecutar mediante sudo -n.' >&2; exit 1; }
[[ $IMAGE == sentinel-cortex:* && $IMAGE != sentinel-cortex:latest ]] || { echo 'Se requiere una imagen Cortex versionada.' >&2; exit 1; }

stream_url=
while IFS= read -r line || [[ -n $line ]]; do
    case $line in
        ''|'#'*) ;;
        MYCNET_STREAM_URL=*) stream_url=${line#MYCNET_STREAM_URL=} ;;
        *) echo 'Campo no autorizado en la plantilla uplink.' >&2; exit 1 ;;
    esac
done < "$REPO_DIR/config/systemd/sentinel-cortex-uplink.env.example"
[[ -n $stream_url ]] || { echo 'Falta MYCNET_STREAM_URL en plantilla.' >&2; exit 1; }

umask 077
readonly STAGED=$(mktemp /etc/sentinel/.backend-uplink.XXXXXX)
trap 'rm -f -- "$STAGED"' EXIT
url_seen=0
image_seen=0
while IFS= read -r line || [[ -n $line ]]; do
    case $line in
        MYCNET_STREAM_URL=*) printf 'MYCNET_STREAM_URL=%s\n' "$stream_url"; url_seen=$((url_seen + 1)) ;;
        SENTINEL_CORTEX_IMAGE=*) printf 'SENTINEL_CORTEX_IMAGE=%s\n' "$IMAGE"; image_seen=$((image_seen + 1)) ;;
        *) printf '%s\n' "$line" ;;
    esac
done < "$TARGET" > "$STAGED"
[[ $url_seen -le 1 && $image_seen -le 1 ]] || { echo 'Claves Cortex duplicadas en backend.env; se preserva el original.' >&2; exit 1; }
[[ $url_seen -ne 0 ]] || printf 'MYCNET_STREAM_URL=%s\n' "$stream_url" >> "$STAGED"
[[ $image_seen -ne 0 ]] || printf 'SENTINEL_CORTEX_IMAGE=%s\n' "$IMAGE" >> "$STAGED"

docker compose --env-file "$STAGED" -f "$REPO_DIR/docker-compose.fenix.yml" config --quiet
readonly BACKUP="$TARGET.pre-cortex-uplink-$(date -u +%Y%m%dT%H%M%SZ)"
cp -a -- "$TARGET" "$BACKUP"
chown root:docker "$STAGED"
chmod 0640 "$STAGED"
mv -f -- "$STAGED" "$TARGET"
printf 'Configuración Cortex instalada; backup: %s\n' "$BACKUP"
