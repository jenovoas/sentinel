#!/usr/bin/env bash
# populate_sentinel_whitelist.sh — Genera y (con --apply) puebla las whitelists
# de Guardian-Alpha LSM (/sys/fs/bpf/sentinel/):
#   1. uid_whitelist_map: root (0) y usuario principal (p. ej. 1000 / jnovoas)
#   2. whitelist_map: ejecutables reales en /proc/*/exe + directorios de sistema
#   3. guardian_mode_map: 0 = auditoría (por defecto), 1 = enforce (solo --enforce)
#
# Uso:
#   ./populate_sentinel_whitelist.sh --dry-run          # Solo inventario y conteo
#   sudo ./populate_sentinel_whitelist.sh --apply       # Puebla mapas en modo auditoría (0)
#   sudo ./populate_sentinel_whitelist.sh --apply --enforce  # Activa modo bloqueo (1)

set -euo pipefail

BPF_DIR="${BPF_DIR:-/sys/fs/bpf/sentinel}"
TARGET_USER="${TARGET_USER:-jnovoas}"
APPLY=0
ENFORCE=0

for arg in "$@"; do
    case "$arg" in
        --dry-run) APPLY=0 ;;
        --apply) APPLY=1 ;;
        --enforce) ENFORCE=1 ;;
        -h|--help)
            sed -n '2,12p' "$0"
            exit 0
            ;;
        *)
            echo "Argumento no reconocido: $arg" >&2
            exit 2
            ;;
    esac
done

# 1. UIDs seguros: root (0) + usuario objetivo
declare -a UIDS=("0")
if id -u "$TARGET_USER" >/dev/null 2>&1; then
    TARGET_UID="$(id -u "$TARGET_USER")"
    if [ "$TARGET_UID" != "0" ]; then
        UIDS+=("$TARGET_UID")
    fi
fi
if [ -n "${EXTRA_UIDS:-}" ]; then
    for u in $EXTRA_UIDS; do
        UIDS+=("$u")
    done
fi
mapfile -t UIDS < <(printf '%s\n' "${UIDS[@]}" | sort -nu)

# 2. Recolectar ejecutables reales (procesos vivos + binarios de sistema)
TMP_LIST="$(mktemp)"
trap 'rm -f "$TMP_LIST"' EXIT

# 2a. Procesos actualmente en ejecución
for exe in /proc/[0-9]*/exe; do
    if [ -L "$exe" ]; then
        target="$(readlink -f "$exe" 2>/dev/null || true)"
        if [ -n "$target" ] && [ -f "$target" ]; then
            echo "$target" >> "$TMP_LIST"
        fi
    fi
done

# 2b. Directorios estándar del sistema y daemons
SEARCH_DIRS=(
    /bin
    /sbin
    /usr/bin
    /usr/sbin
    /usr/local/bin
    /usr/local/sbin
    /usr/lib/systemd
    /usr/libexec
    /usr/lib/openssh
    /usr/lib/git-core
    /usr/lib/apt/methods
    /usr/lib/postgresql
    /usr/lib/samba
)

for d in "${SEARCH_DIRS[@]}"; do
    if [ -d "$d" ]; then
        find "$d" -maxdepth 3 \( -type f -o -type l \) -executable 2>/dev/null | while IFS= read -r p; do
            echo "$p"
            resolved="$(readlink -f "$p" 2>/dev/null || true)"
            if [ -n "$resolved" ] && [ -f "$resolved" ]; then
                echo "$resolved"
            fi
        done >> "$TMP_LIST"
    fi
done

# Filtrar: rutas absolutas < 256 bytes, existentes, nunca /tmp o /dev/shm, únicas
mapfile -t PATHS < <(
    python3 - "$TMP_LIST" <<'PY'
import os, sys

seen = set()
with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        p = line.strip()
        if not p.startswith("/"):
            continue
        if p.startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
            continue
        if len(p.encode("utf-8")) >= 256:
            continue
        if not os.path.isfile(p):
            continue
        if p not in seen:
            seen.add(p)

for p in sorted(seen):
    print(p)
PY
)

COUNT="${#PATHS[@]}"
echo "UIDs seguros (${#UIDS[@]}): ${UIDS[*]}"
echo "Binarios del sistema recolectados: $COUNT (límite del mapa: 10000)"

if [ "$COUNT" -gt 10000 ]; then
    echo "ERROR: $COUNT supera max_entries=10000 de whitelist_map" >&2
    exit 1
fi

if [ "$APPLY" -eq 0 ]; then
    echo "Modo --dry-run: no se modificó $BPF_DIR."
    echo "Muestra (primeras 10 rutas):"
    printf '  %s\n' "${PATHS[@]:0:10}"
    exit 0
fi

# 3. Aplicar a los mapas pinned en $BPF_DIR
for m in uid_whitelist_map whitelist_map guardian_mode_map; do
    if [ ! -e "$BPF_DIR/$m" ]; then
        echo "ERROR: falta el mapa pinned $BPF_DIR/$m" >&2
        exit 1
    fi
done

BATCH_FILE="$(mktemp)"
trap 'rm -f "$TMP_LIST" "$BATCH_FILE"' EXIT

python3 - "$BATCH_FILE" "$BPF_DIR" "$ENFORCE" "${UIDS[@]}" -- "${PATHS[@]}" <<'PY'
import struct, sys

batch_path = sys.argv[1]
bpf_dir = sys.argv[2]
enforce = int(sys.argv[3])
rest = sys.argv[4:]
sep = rest.index("--")
uids = [int(u) for u in rest[:sep]]
paths = rest[sep + 1:]

def hex_bytes(b: bytes) -> str:
    return " ".join(f"{x:02x}" for x in b)

with open(batch_path, "w", encoding="utf-8") as out:
    # Mode map: key 0 (4 bytes LE) -> 0 (audit) or 1 (enforce)
    out.write(
        f"map update pinned {bpf_dir}/guardian_mode_map "
        f"key hex 00 00 00 00 value hex {enforce:02x}\n"
    )
    # UID whitelist
    for uid in uids:
        k = struct.pack("<I", uid)
        out.write(
            f"map update pinned {bpf_dir}/uid_whitelist_map "
            f"key hex {hex_bytes(k)} value hex 01\n"
        )
    # Path whitelist (char[256] zero-padded)
    for p in paths:
        raw = p.encode("utf-8")
        padded = raw + b"\x00" * (256 - len(raw))
        out.write(
            f"map update pinned {bpf_dir}/whitelist_map "
            f"key hex {hex_bytes(padded)} value hex 01\n"
        )
PY

bpftool batch file "$BATCH_FILE"
echo "Whitelist poblada en $BPF_DIR: ${#UIDS[@]} UIDs, $COUNT rutas, mode=$ENFORCE."
