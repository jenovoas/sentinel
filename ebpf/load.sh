#!/bin/bash
# Sentinel eBPF - Cargador completo de todos los módulos
set -e

BOLD='\033[1m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
IFACE=eth0

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; }

cd "$(dirname "$0")"

# ─── LSM ──────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}── LSM Programs ──────────────────────────────────────────${NC}"
for prog in guardian_alpha_lsm lsm_ai_guardian ai_guardian guardian_cognitive float_detector; do
    pin="/sys/fs/bpf/$prog"
    obj="$prog.o"
    if [ ! -f "$obj" ]; then
        err "$obj no encontrado — ejecuta 'make' primero"; exit 1
    fi
    [ -f "$pin" ] && sudo rm -f "$pin"
    sudo bpftool prog load "$obj" "$pin" type lsm && ok "$prog cargado" || err "fallo al cargar $prog"
done

# ─── XDP ──────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}── XDP Programs ──────────────────────────────────────────${NC}"
for obj in burst_sensor.o xdp_firewall.o; do
    if [ ! -f "$obj" ]; then
        warn "$obj no encontrado — saltando"; continue
    fi
    sudo ip link set dev $IFACE xdp obj "$obj" sec xdp && ok "$obj anclado en $IFACE" \
        || err "fallo XDP $obj (¿otro XDP activo en $IFACE?)"
done

# ─── TC ───────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}── TC Programs ───────────────────────────────────────────${NC}"
if [ -f tc_firewall.o ]; then
    sudo tc qdisc add dev $IFACE clsact 2>/dev/null || true
    sudo tc filter add dev $IFACE ingress bpf da obj tc_firewall.o sec tc \
        && ok "tc_firewall anclado en $IFACE" || err "fallo TC"
else
    warn "tc_firewall.o no encontrado — saltando"
fi

# ─── Estado final ─────────────────────────────────────────────────────────────
echo -e "\n${BOLD}── Estado ────────────────────────────────────────────────${NC}"
sudo bpftool prog list | grep -E "lsm|xdp|tc" | awk '{print "  " $0}' || warn "sin programas eBPF activos"
echo ""
