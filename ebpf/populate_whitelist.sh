#!/bin/bash
# populate_whitelist.sh — Pre-poblar Guardian-Alpha LSM whitelist_map
#
# Diseñado por: Claude (arquitecto)
# Ejecutar en: nodo sentinel, ANTES de cargar guardian_alpha_lsm.o
#
# MECANISMO:
#   1. Crea el mapa BPF pinned en /sys/fs/bpf/sentinel/whitelist_map
#   2. Puebla con todos los binarios necesarios
#   3. En Fase 4, bpftool prog load reutiliza este mapa pre-poblado
#
# TIPO DE MAPA: BPF_MAP_TYPE_HASH
#   key:   char[256] — path en UTF-8, zero-padded a 256 bytes (hex)
#   value: __u8      — 1 = allowed (hex: 01)

set -e

BPF_SENTINEL_DIR="/sys/fs/bpf/sentinel"
MAP_PIN="${BPF_SENTINEL_DIR}/whitelist_map"
LOG_FILE="/tmp/populate_whitelist.log"

# --- Colores ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()   { echo -e "${GREEN}[+]${NC} $1" | tee -a "$LOG_FILE"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"; exit 1; }

# --- Verificaciones previas ---
[[ $EUID -ne 0 ]] && error "Este script debe correr como root (sudo)"
command -v bpftool >/dev/null 2>&1 || error "bpftool no encontrado"
command -v python3 >/dev/null 2>&1 || error "python3 no encontrado"
mount | grep -q "bpffs\|/sys/fs/bpf" || error "BPF filesystem no montado en /sys/fs/bpf"

echo "=============================================="
echo " Guardian-Alpha — Whitelist Pre-population"
echo "=============================================="
echo "" | tee "$LOG_FILE"

# --- Crear directorio BPF de Sentinel ---
log "Creando directorio ${BPF_SENTINEL_DIR}..."
mkdir -p "${BPF_SENTINEL_DIR}"

# --- Eliminar mapa anterior si existe ---
if [ -e "${MAP_PIN}" ]; then
    warn "whitelist_map ya existe en ${MAP_PIN}. Eliminando..."
    rm -f "${MAP_PIN}"
fi

# --- Crear el mapa pinned ---
log "Creando whitelist_map (BPF_MAP_TYPE_HASH, key=256, value=1, entries=10000)..."
bpftool map create "${MAP_PIN}" \
    type hash \
    key 256 \
    value 1 \
    entries 10000 \
    name whitelist_map

log "Mapa creado en ${MAP_PIN}"

# --- Función para agregar un path al whitelist ---
# Convierte path a 256 bytes hex (null-padded) y actualiza el mapa
add_to_whitelist() {
    local path="$1"
    local description="${2:-}"

    # Verificar que el path no es demasiado largo (max 255 chars + null)
    if [ ${#path} -gt 255 ]; then
        warn "Path demasiado largo (>${PATH_MAX}-1 chars), ignorado: $path"
        return
    fi

    # Generar key hex de 256 bytes usando Python
    local key_hex
    key_hex=$(python3 -c "
path = '$path'
key_bytes = path.encode('utf-8') + b'\\x00' * (256 - len(path))
print(' '.join(f'{b:02x}' for b in key_bytes))
" 2>/dev/null)

    if [ -z "$key_hex" ]; then
        warn "No se pudo generar hex para: $path"
        return
    fi

    # Actualizar mapa
    if bpftool map update pinned "${MAP_PIN}" key hex $key_hex value hex 01 2>/dev/null; then
        echo "  ADDED: $path" | tee -a "$LOG_FILE"
    else
        warn "Fallo al agregar: $path"
    fi
}

# --- Agregar binario solo si existe en el sistema ---
add_if_exists() {
    local path="$1"
    if [ -f "$path" ] && [ -x "$path" ]; then
        add_to_whitelist "$path"
    else
        echo "  SKIP (no existe): $path" | tee -a "$LOG_FILE"
    fi
}

# =============================================================================
# BLOQUE 1: Sistema base — críticos para que el OS funcione
# =============================================================================
log "Poblando: Sistema base..."

add_if_exists "/usr/bin/bash"
add_if_exists "/usr/bin/sh"
add_if_exists "/usr/bin/dash"
add_if_exists "/bin/bash"          # symlink → /usr/bin/bash (ambas formas)
add_if_exists "/bin/sh"
add_if_exists "/bin/dash"
add_if_exists "/usr/bin/sudo"
add_if_exists "/usr/sbin/sudo"
add_if_exists "/usr/bin/env"
add_if_exists "/usr/bin/systemctl"
add_if_exists "/usr/bin/journalctl"
add_if_exists "/usr/bin/loginctl"
add_if_exists "/usr/lib/systemd/systemd"
add_if_exists "/usr/sbin/init"
add_if_exists "/sbin/init"

# =============================================================================
# BLOQUE 2: SSH
# =============================================================================
log "Poblando: SSH..."

add_if_exists "/usr/sbin/sshd"
add_if_exists "/usr/bin/ssh"
add_if_exists "/usr/bin/scp"
add_if_exists "/usr/bin/sftp"
add_if_exists "/usr/lib/openssh/sftp-server"

# =============================================================================
# BLOQUE 3: Samba AD DC
# =============================================================================
log "Poblando: Samba AD DC..."

# Binarios principales
for bin in samba smbd nmbd winbindd samba-gpupdate samba_dnsupdate \
           samba_kcc samba_spnupdate samba_upgradedns samba-tool samba-gpupdate; do
    add_if_exists "/usr/sbin/${bin}"
    add_if_exists "/usr/bin/${bin}"
done

# Helpers en /usr/lib/samba/
if [ -d "/usr/lib/samba/" ]; then
    log "  Escaneando binarios en /usr/lib/samba/..."
    while IFS= read -r -d '' bin; do
        add_to_whitelist "$bin"
    done < <(find /usr/lib/samba/ -maxdepth 3 -type f -executable -print0 2>/dev/null)
fi

# libexec de samba
if [ -d "/usr/libexec/samba/" ]; then
    while IFS= read -r -d '' bin; do
        add_to_whitelist "$bin"
    done < <(find /usr/libexec/samba/ -maxdepth 3 -type f -executable -print0 2>/dev/null)
fi

# =============================================================================
# BLOQUE 4: PowerDNS
# =============================================================================
log "Poblando: PowerDNS..."

add_if_exists "/usr/sbin/pdns_server"
add_if_exists "/usr/sbin/pdns-recursor"
add_if_exists "/usr/bin/pdns_control"
add_if_exists "/usr/bin/pdns_client"
add_if_exists "/usr/bin/rec_control"

# =============================================================================
# BLOQUE 5: Chrony / NTP
# =============================================================================
log "Poblando: Chrony NTP..."

add_if_exists "/usr/sbin/chronyd"
add_if_exists "/usr/bin/chronyc"

# =============================================================================
# BLOQUE 6: WireGuard VPN
# =============================================================================
log "Poblando: WireGuard..."

add_if_exists "/usr/bin/wg"
add_if_exists "/usr/sbin/wg-quick"
add_if_exists "/usr/bin/wg-quick"

# =============================================================================
# BLOQUE 7: auditd
# =============================================================================
log "Poblando: auditd..."

add_if_exists "/usr/sbin/auditd"
add_if_exists "/sbin/auditd"
add_if_exists "/usr/sbin/auditctl"
add_if_exists "/sbin/auditctl"
add_if_exists "/usr/sbin/aureport"
add_if_exists "/usr/sbin/ausearch"
add_if_exists "/usr/sbin/augenrules"
add_if_exists "/usr/sbin/audispd"
add_if_exists "/usr/sbin/audisp-af_unix"
add_if_exists "/usr/sbin/audisp-remote"
add_if_exists "/usr/lib/audisp/audispd"
add_if_exists "/usr/libexec/audit/audispd"

# =============================================================================
# BLOQUE 8: Container runtime (Podman + compat Docker)
# =============================================================================
log "Poblando: Podman / Docker compat..."

add_if_exists "/usr/bin/podman"
add_if_exists "/usr/bin/podman-compose"
add_if_exists "/usr/bin/docker"
add_if_exists "/usr/bin/docker-compose"
add_if_exists "/usr/bin/containerd"
add_if_exists "/usr/sbin/containerd"
add_if_exists "/usr/bin/containerd-shim"
add_if_exists "/usr/bin/containerd-shim-runc-v2"
add_if_exists "/usr/sbin/runc"
add_if_exists "/usr/bin/runc"
add_if_exists "/usr/libexec/podman/conmon"
add_if_exists "/usr/bin/conmon"
add_if_exists "/usr/libexec/cni/bridge"
add_if_exists "/usr/lib/cni/bridge"
add_if_exists "/usr/bin/slirp4netns"
add_if_exists "/usr/bin/fuse-overlayfs"
add_if_exists "/usr/bin/newuidmap"
add_if_exists "/usr/bin/newgidmap"
add_if_exists "/usr/sbin/newuidmap"
add_if_exists "/usr/sbin/newgidmap"

# =============================================================================
# BLOQUE 9: Python (backend FastAPI + scripts)
# =============================================================================
log "Poblando: Python..."

add_if_exists "/usr/bin/python3"
add_if_exists "/usr/bin/python3.12"   # Debian 13 trixie default
add_if_exists "/usr/bin/python3.11"   # Fallback
add_if_exists "/usr/bin/python3.13"   # Futuro
add_if_exists "/usr/bin/pip3"
add_if_exists "/usr/bin/pip"

# =============================================================================
# BLOQUE 10: Node.js (frontend Next.js)
# =============================================================================
log "Poblando: Node.js..."

add_if_exists "/usr/bin/node"
add_if_exists "/usr/local/bin/node"
add_if_exists "/usr/bin/npm"
add_if_exists "/usr/bin/npx"
add_if_exists "/usr/local/bin/npm"

# =============================================================================
# BLOQUE 11: Utilidades de red y sistema
# =============================================================================
log "Poblando: Utilidades de sistema y red..."

for bin in curl wget rsync ip ss nft iptables ip6tables \
           grep awk sed cut sort uniq tr head tail cat less \
           ls cp mv rm mkdir rmdir ln chmod chown chgrp \
           find xargs basename dirname readlink realpath \
           tar gzip gunzip bzip2 xz zip unzip \
           openssl gpg gpg2 \
           ps top htop kill killall pkill \
           id whoami groups getent \
           mount umount df du lsblk \
           ping ping6 traceroute \
           hostname hostnamectl timedatectl \
           apt apt-get apt-cache dpkg dpkg-query \
           systemd-resolve resolvectl \
           logger logrotate \
           cron crond \
           jq xmllint \
           strace ltrace gdb \
           make gcc g++ cc; do
    add_if_exists "/usr/bin/${bin}"
    add_if_exists "/bin/${bin}"
    add_if_exists "/usr/sbin/${bin}"
    add_if_exists "/sbin/${bin}"
done

# =============================================================================
# BLOQUE 12: bpftool (Sentinel lo necesita)
# =============================================================================
log "Poblando: bpftool..."

add_if_exists "/usr/sbin/bpftool"
add_if_exists "/usr/bin/bpftool"
# También puede estar en linux-tools path
bpftool_path=$(which bpftool 2>/dev/null)
[ -n "$bpftool_path" ] && add_to_whitelist "$bpftool_path"

# =============================================================================
# BLOQUE 13: Servicios systemd de Sentinel (watchdog scripts)
# =============================================================================
log "Poblando: Scripts Sentinel host..."

# Si los watchdog scripts son shell scripts o binarios
for script in /home/jnovoas/Dev/sentinel/host-metrics/audit-watchdog.sh \
              /home/jnovoas/Dev/sentinel/host-metrics/scripts/*.sh; do
    [ -f "$script" ] && [ -x "$script" ] && add_to_whitelist "$script"
done

# =============================================================================
# RESUMEN
# =============================================================================
echo ""
log "=============================================="
TOTAL=$(bpftool map dump pinned "${MAP_PIN}" 2>/dev/null | grep -c '"key"' || echo "?")
log "Whitelist poblado: ${TOTAL} entradas en ${MAP_PIN}"
log "Log completo: ${LOG_FILE}"
echo ""
warn "VERIFICAR antes de cargar el LSM:"
warn "  sudo bpftool map dump pinned ${MAP_PIN} | python3 -c \\"
warn "  \"import sys,json; data=json.load(sys.stdin); print(len(data), 'entries')\""
echo ""
log "Para cargar el LSM con este mapa pre-poblado, ejecutar Fase 4:"
log "  sudo bpftool prog load ~/Dev/sentinel/ebpf/guardian_alpha_lsm.o \\"
log "    /sys/fs/bpf/guardian_alpha_lsm type lsm \\"
log "    map name whitelist_map pinned ${MAP_PIN}"
echo "=============================================="
