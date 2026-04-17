#!/bin/bash
# populate_float_whitelist.sh — Espeja whitelist_map → float_safe_map
#
# Estrategia: reutilizar la whitelist ya curada de Guardian-Alpha.
# El conjunto de binarios "autorizados para ejecutar" es el mismo
# conjunto "S60-safe" por construcción: Sentinel solo autoriza binarios
# auditados, y esos son los mismos que no deben ser flaggeados por
# float_detector.
#
# Pre-requisito: correr populate_whitelist.sh ANTES (pobla whitelist_map).
#
# Uso: sudo ./populate_float_whitelist.sh

set -e

SRC_MAP="/sys/fs/bpf/sentinel/whitelist_map"
DST_MAP="/sys/fs/bpf/sentinel/float_safe_map"
DST_DIR="$(dirname "$DST_MAP")"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log()  { echo -e "${GREEN}[+]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

[[ $EUID -ne 0 ]] && err "Ejecutar como root (sudo)"
command -v bpftool >/dev/null || err "bpftool no encontrado"
command -v python3 >/dev/null || err "python3 no encontrado"
[ -e "$SRC_MAP" ] || err "$SRC_MAP no existe. Corre populate_whitelist.sh primero."

mkdir -p "$DST_DIR"

# Crear o recrear mapa destino
if [ -e "$DST_MAP" ]; then
    warn "float_safe_map ya existe. Recreando..."
    rm -f "$DST_MAP"
fi

log "Creando float_safe_map (hash, key=256, value=1, entries=4096)..."
bpftool map create "$DST_MAP" \
    type hash \
    key 256 \
    value 1 \
    entries 4096 \
    name float_safe_map

# Mirror de entradas
log "Espejando entradas de whitelist_map → float_safe_map..."
python3 <<PYEOF
import json, subprocess, sys

src = subprocess.run(
    ["bpftool", "-j", "map", "dump", "pinned", "$SRC_MAP"],
    capture_output=True, text=True, check=True,
)
entries = json.loads(src.stdout)
copied = 0
for e in entries:
    key = e["key"]    # list of "0xNN" hex strings
    val = e["value"]
    cmd = ["bpftool", "map", "update", "pinned", "$DST_MAP",
           "key", "hex", *(k.replace("0x", "") for k in key),
           "value", "hex", *(v.replace("0x", "") for v in val)]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        copied += 1
    except subprocess.CalledProcessError as err:
        print(f"  WARN: fallo en entrada: {err.stderr.decode()}", file=sys.stderr)
print(f"  {copied} entradas copiadas")
PYEOF

TOTAL=$(bpftool -j map dump pinned "$DST_MAP" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
log "float_safe_map poblado: $TOTAL entradas"
log "Para cargar float_detector con este mapa pre-poblado:"
echo "  sudo bpftool prog load float_detector.o /sys/fs/bpf/float_detector type lsm \\"
echo "    map name float_safe_map pinned $DST_MAP"
