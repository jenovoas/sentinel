#!/bin/bash
set -e

echo "=============================================="
echo " Guardian-Alpha LSM - Reload Completo"
echo "=============================================="

# 1. Crear directorio BPF
mkdir -p /sys/fs/bpf/sentinel

# 2. Lista de binarios criticos
BINARIES=(
  "/usr/lib/systemd/systemd"
  "/usr/bin/systemctl"
  "/bin/bash"
  "/bin/sh"
  "/usr/bin/zsh"
  "/usr/sbin/sshd"
  "/usr/bin/ssh"
  "/usr/sbin/samba"
  "/usr/sbin/smbd"
  "/usr/sbin/winbindd"
  "/usr/bin/samba-tool"
  "/usr/bin/wbinfo"
  "/usr/bin/net"
  "/usr/bin/kinit"
  "/usr/bin/klist"
  "/usr/bin/podman"
  "/usr/bin/crun"
  "/usr/sbin/auditd"
  "/usr/bin/ausearch"
  "/usr/sbin/ip"
  "/usr/sbin/nft"
  "/usr/bin/wg"
  "/usr/bin/wg-quick"
  "/usr/bin/python3"
  "/usr/bin/node"
  "/usr/bin/vim"
  "/usr/bin/nvim"
  "/usr/bin/git"
  "/usr/bin/tmux"
  "/usr/bin/htop"
  "/home/jnovoas/Dev/sentinel/host-metrics/audit-watchdog.sh"
  "/home/jnovoas/Dev/sentinel/host-metrics/audit-watchdog-s60.sh"
)

# 3. Crear mapa y poblar
echo "Creando whitelist_map..."
bpftool map create /sys/fs/bpf/sentinel/whitelist_map type hash key 256 value 1 max_entries 10000 2>/dev/null || echo "Mapa ya existe"

echo "Poblando whitelist..."
COUNT=0
for bin in "${BINARIES[@]}"; do
  if [[ -x "$bin" ]]; then
    # Convertir path a key hex
    key=$(python3 -c "p=b'$bin'; p=p[:255]+b'\x00'*(256-len(p)); print(p.hex())")
    if bpftool map update pinned /sys/fs/bpf/sentinel/whitelist_map key hex "$key" value hex 01 2>/dev/null; then
      echo "  ADDED: $bin"
      COUNT=$((COUNT + 1))
    fi
  fi
done

echo ""
echo "Entradas agregadas: $COUNT"

# 4. Cargar LSM reutilizando el mapa
echo ""
echo "Cargando Guardian-Alpha LSM..."
cd /home/jnovoas/Dev/sentinel/ebpf
bpftool prog load guardian_alpha_lsm.o /sys/fs/bpf/guardian_alpha_lsm type lsm

echo ""
echo "Verificando..."
bpftool prog list | grep -E "guardian|lsm" || true

MAP_ID=$(bpftool map list | grep whitelist_map | head -1 | cut -d: -f1 | tr -d ' ')
if [[ -n "$MAP_ID" ]]; then
 _entries=$(bpftool map dump id $MAP_ID --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d))" 2>/dev/null || echo "0")
  echo "whitelist_map tiene $_entries entradas"
fi

echo ""
echo "=============================================="
echo " Guardian-Alpha LSM - Ring 0 ACTIVO"
echo "=============================================="
