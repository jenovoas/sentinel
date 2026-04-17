#!/bin/bash
# Sentinel eBPF - Descarga completa de todos los módulos
BOLD='\033[1m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
IFACE=eth0

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }

echo -e "\n${BOLD}── Gamma (descargar PRIMERO para no disparar falsos PEER_VANISHED) ──${NC}"
# Matar watchdog userspace antes que los pins del kernel
if [ -f /var/run/sentinel/gamma.pid ]; then
    PID=$(cat /var/run/sentinel/gamma.pid)
    sudo kill -TERM "$PID" 2>/dev/null && ok "gamma_watchdog (pid=$PID) terminado"
    sudo rm -f /var/run/sentinel/gamma.pid
else
    sudo pkill -f gamma_watchdog 2>/dev/null && ok "gamma_watchdog terminado (pkill)"
fi
if [ -d /sys/fs/bpf/sentinel/gamma ]; then
    sudo rm -rf /sys/fs/bpf/sentinel/gamma && ok "gamma kernel pins eliminados"
fi
# Limpiar maps pineados de Gamma (LIBBPF_PIN_BY_NAME → /sys/fs/bpf/<name>)
sudo rm -f /sys/fs/bpf/known_peer_prog_ids \
           /sys/fs/bpf/gamma_heartbeat \
           /sys/fs/bpf/rate_limit \
           /sys/fs/bpf/events 2>/dev/null || true

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
