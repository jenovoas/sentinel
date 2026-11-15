#!/usr/bin/env bash
# load_sentinel_passive.sh — Carga y adjunta Guardian-Alpha LSM en modo PASIVO
# (guardian_mode_map[0] = 0: observa y registra lo que bloquearía, SIN devolver -EACCES).
#
# Uso en el nodo objetivo (p. ej. kingu):
#   sudo bash ebpf/load_sentinel_passive.sh
#
# Observar qué bloquearía:
#   sudo grep -E "WOULD BLOCK|AUDIT-ISOLATION" /sys/kernel/debug/tracing/trace_pipe
#
# Descargar completamente:
#   sudo rm -rf /sys/fs/bpf/sentinel

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROG="$SCRIPT_DIR/guardian_alpha_lsm.o"
BPF_DIR="${BPF_DIR:-/sys/fs/bpf/sentinel}"
PIN="$BPF_DIR/guardian_prog"
LINK_PIN="$BPF_DIR/guardian_link"

if [ ! -f "$PROG" ]; then
    echo "Compilando guardian_alpha_lsm.o..."
    make -C "$SCRIPT_DIR" guardian_alpha_lsm.o
fi

if [ ! -x "$SCRIPT_DIR/attacher" ]; then
    echo "Compilando attacher..."
    clang -g -O2 -Wall -I/usr/include -o "$SCRIPT_DIR/attacher" "$SCRIPT_DIR/attacher.c" -lbpf
fi

mkdir -p "$BPF_DIR"

if [ -e "$PIN" ] || [ -e "$LINK_PIN" ]; then
    echo "Limpiando pins previos en $BPF_DIR..."
    rm -rf "$BPF_DIR"/*
fi

echo "Cargando $PROG (modo pasivo por defecto: guardian_mode_map[0]=0)..."
bpftool prog load "$PROG" "$PIN" type lsm pinmaps "$BPF_DIR"

echo "Poblando whitelist (UIDs seguros + binarios del host, modo=0)..."
BPF_DIR="$BPF_DIR" bash "$SCRIPT_DIR/populate_sentinel_whitelist.sh" --apply

echo "Adjuntando LSM en modo pasivo..."
"$SCRIPT_DIR/attacher" "$PIN" "$LINK_PIN"

echo ""
echo "Guardian-Alpha activo en MODO PASIVO (0 = solo auditoría, sin bloqueos)."
echo "Ver modo actual (debe terminar en 00):"
echo "  sudo bpftool map dump pinned $BPF_DIR/guardian_mode_map"
echo "Observar qué habría bloqueado:"
echo "  sudo grep -E 'WOULD BLOCK|AUDIT-ISOLATION' /sys/kernel/debug/tracing/trace_pipe"
echo "Desactivar:"
echo "  sudo rm -rf $BPF_DIR"
