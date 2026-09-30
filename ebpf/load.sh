#!/bin/bash
# Sentinel eBPF - Cargador completo de todos los módulos
set -e

BOLD='\033[1m'; GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'; NC='\033[0m'
IFACE=eth0

ok()   { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
err()  { echo -e "${RED}❌ $*${NC}"; }

cd "$(dirname "$0")"

# Make the finite boot action deterministic after a prior partial load.
sudo pkill -f gamma_watchdog 2>/dev/null || true
sudo bpftool net detach xdp dev "$IFACE" 2>/dev/null || true
sudo rm -rf /sys/fs/bpf/sentinel/gamma
sudo rm -f /sys/fs/bpf/known_peer_prog_ids \
    /sys/fs/bpf/gamma_heartbeat /sys/fs/bpf/rate_limit /sys/fs/bpf/events \
    /sys/fs/bpf/sentinel/events /sys/fs/bpf/xdp_firewall_xdp \
    /sys/fs/bpf/tc_firewall

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
for obj in xdp_firewall.o; do
    if [ ! -f "$obj" ]; then
        warn "$obj no encontrado — saltando"; continue
    fi
    if sudo ip link set dev "$IFACE" xdp obj "$obj" sec xdp; then
        ok "$obj anclado en $IFACE"
    elif sudo bpftool prog load "$obj" "/sys/fs/bpf/${obj%.o}_xdp" type xdp \
         && sudo bpftool net attach xdp pinned "/sys/fs/bpf/${obj%.o}_xdp" dev "$IFACE"; then
        ok "$obj cargado/anclado vía bpftool en $IFACE"
    else
        err "fallo XDP $obj (¿otro XDP activo en $IFACE?)"
    fi
done

# ─── TC ───────────────────────────────────────────────────────────────────────
echo -e "\n${BOLD}── TC Programs ───────────────────────────────────────────${NC}"
if [ -f tc_firewall.o ]; then
    sudo tc qdisc add dev "$IFACE" clsact 2>/dev/null || true
    sudo tc filter del dev "$IFACE" ingress 2>/dev/null || true
    sudo rm -f /sys/fs/bpf/tc_firewall
    sudo bpftool prog load tc_firewall.o /sys/fs/bpf/tc_firewall type classifier \
        && sudo tc filter add dev "$IFACE" ingress bpf da pinned /sys/fs/bpf/tc_firewall \
        && ok "tc_firewall anclado en $IFACE" || err "fallo TC"
else
    warn "tc_firewall.o no encontrado — saltando"
fi

# ─── Gamma (meta-vigilancia, cargar al final) ─────────────────────────────────
echo -e "\n${BOLD}── Meta-Guardian (Gamma) ─────────────────────────────────${NC}"
if [ -f guardian_gamma.o ]; then
    sudo mkdir -p /sys/fs/bpf/sentinel
    if sudo bpftool prog loadall guardian_gamma.o /sys/fs/bpf/sentinel/gamma \
         autoattach pinmaps /sys/fs/bpf 2>/dev/null; then
        if [ ! -e /sys/fs/bpf/sentinel/events ]; then
            events_id="$(sudo bpftool map show pinned /sys/fs/bpf/events \
                | awk 'NR == 1 { sub(/:/, "", $1); print $1 }')"
            sudo bpftool map pin id "$events_id" /sys/fs/bpf/sentinel/events
        fi
        ok "guardian_gamma cargado (kprobes activos)"
    else
        err "fallo al cargar guardian_gamma"
    fi

    # Lanzar watchdog userspace
    if [ -x ./gamma_watchdog ]; then
        sudo mkdir -p /var/log/sentinel /var/run/sentinel
        sudo pkill -f gamma_watchdog 2>/dev/null || true
        sudo nohup ./gamma_watchdog \
            >>/var/log/sentinel/gamma.ndjson 2>>/var/log/sentinel/gamma.err &
        echo $! | sudo tee /var/run/sentinel/gamma.pid >/dev/null
        sleep 0.5
        if sudo kill -0 "$(cat /var/run/sentinel/gamma.pid)" 2>/dev/null; then
            ok "gamma_watchdog activo (pid=$(cat /var/run/sentinel/gamma.pid))"
        else
            err "gamma_watchdog no arrancó — ver /var/log/sentinel/gamma.err"
        fi
    else
        warn "gamma_watchdog binario no encontrado — ejecuta 'make'"
    fi
else
    warn "guardian_gamma.o no encontrado — saltando"
fi

# ─── Estado final ─────────────────────────────────────────────────────────────
echo -e "\n${BOLD}── Estado ────────────────────────────────────────────────${NC}"
sudo bpftool prog list | grep -E "lsm|xdp|tc|kprobe" | awk '{print "  " $0}' || warn "sin programas eBPF activos"
echo ""
