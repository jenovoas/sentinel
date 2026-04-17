#!/bin/bash
# Sentinel eBPF - Descarga completa de todos los módulos
BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
IFACE=eth0

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

echo -e "\n${BOLD}── LSM pins ──────────────────────────────────────────────${NC}"
for prog in guardian_alpha_lsm lsm_ai_guardian ai_guardian guardian_cognitive float_detector; do
    pin="/sys/fs/bpf/$prog"
    if [ -f "$pin" ]; then
        sudo rm -f "$pin" && ok "$prog pin eliminado"
    fi
done
warn "LSM permanece en kernel hasta reboot (comportamiento normal)"

echo -e "\n${BOLD}── XDP ───────────────────────────────────────────────────${NC}"
sudo ip link set dev $IFACE xdp off 2>/dev/null && ok "XDP desanclado de $IFACE" || warn "sin XDP activo"

echo -e "\n${BOLD}── TC ────────────────────────────────────────────────────${NC}"
sudo tc qdisc del dev $IFACE clsact 2>/dev/null && ok "TC clsact eliminado" || warn "sin TC activo"

echo -e "\n${BOLD}── Estado final ──────────────────────────────────────────${NC}"
sudo bpftool prog list | grep -E "guardian|burst|firewall" | awk '{print "  " $0}' || ok "sin programas Sentinel activos"
echo ""
