#!/usr/bin/env bash
# mesh_setup.sh — Setup completo de la mesh batman-adv sobre WireGuard + VXLAN
# Uso: ./mesh_setup.sh <node_number> <remote_public_ip> <wg_port>
#   node_number: 1 = laptop, 2 = Fan
#   remote_public_ip: IP pública del otro nodo
#   wg_port: puerto WireGuard del otro nodo
#
# Ejemplo:
#   Laptop: ./mesh_setup.sh 1 157.254.174.40 51820
#   Fan:    ./mesh_setup.sh 2 191.116.111.112 51820

set -euo pipefail

NODE_NUM="${1:?Uso: $0 <node_number> <remote_public_ip> [wg_port]}"
REMOTE_PUB="${2:?Falta IP pública del otro nodo}"
WG_PORT="${3:-51820}"

WG_SUBNET="10.88.0"
MESH_SUBNET="10.10.0"
VXLAN_ID=42

case "$NODE_NUM" in
    1) NODE_NAME="laptop"; WG_IP="${WG_SUBNET}.2"; MESH_IP="${MESH_SUBNET}.11" ;;
    2) NODE_NAME="fan";    WG_IP="${WG_SUBNET}.1"; MESH_IP="${MESH_SUBNET}.12" ;;
    *) echo "Error: node_number debe ser 1 (laptop) o 2 (Fan)"; exit 1 ;;
esac

echo "═══════════════════════════════════════════════"
echo "  Mesh Setup — $NODE_NAME (n$NODE_NUM)"
echo "  WG IP: $WG_IP/24"
echo "  Mesh IP: $MESH_IP/24"
echo "═══════════════════════════════════════════════"

OS=""
[ -f /etc/os-release ] && . /etc/os-release && OS="$ID"

# ─── 1. Instalar dependencias ──────────────────────────────────────────────
echo ""
echo "📦 Instalando dependencias..."

# WireGuard tools
if ! command -v wg &>/dev/null; then
    case "$OS" in
        fedora) sudo dnf install -y wireguard-tools ;;
        rocky|rhel) sudo dnf install -y wireguard-tools ;;
    esac
fi

# batctl + dependencias batman-adv
if ! command -v batctl &>/dev/null; then
    case "$OS" in
        fedora) sudo dnf install -y batctl ;;
        rocky|rhel) sudo dnf install -y libnl3-devel
            echo "   ⚠️  batman-adv debe compilarse manualmente en Rocky. Ver scripts/mesh/README" ;;
    esac
fi

# ─── 2. Generar claves WireGuard (si no existen) ───────────────────────────
echo ""
echo "🔑 Generando claves WireGuard..."
mkdir -p /tmp/wg
if [ ! -f /tmp/wg/node-priv ]; then
    wg genkey | tee /tmp/wg/node-priv | wg pubkey > /tmp/wg/node-pub
fi
echo "   Pub key: $(cat /tmp/wg/node-pub)"

# ─── 3. Configurar WireGuard ───────────────────────────────────────────────
echo ""
echo "🔗 Configurando WireGuard..."

if [ "$NODE_NUM" = "1" ]; then
    # Laptop: cliente
    sudo tee /etc/wireguard/wg0.conf > /dev/null << WGEOF
[Interface]
PrivateKey = $(cat /tmp/wg/node-priv)
Address = ${WG_IP}/24

[Peer]
PublicKey = ${FAN_PUBKEY:-CHANGEME_FAN_PUBKEY}
Endpoint = ${REMOTE_PUB}:${WG_PORT}
AllowedIPs = ${WG_SUBNET}.0/24
PersistentKeepalive = 25
WGEOF
else
    # Fan: servidor
    sudo tee /etc/wireguard/wg0.conf > /dev/null << WGEOF
[Interface]
PrivateKey = $(cat /tmp/wg/node-priv)
Address = ${WG_IP}/24
ListenPort = ${WG_PORT}

[Peer]
PublicKey = ${LAPTOP_PUBKEY:-CHANGEME_LAPTOP_PUBKEY}
AllowedIPs = ${WG_SUBNET}.0/24
WGEOF
fi

sudo chmod 600 /etc/wireguard/wg0.conf
echo "   Config en /etc/wireguard/wg0.conf"

# ─── 4. Levantar WireGuard ─────────────────────────────────────────────────
sudo wg-quick up wg0 2>/dev/null || sudo systemctl enable --now wg-quick@wg0
sleep 2
echo "   Estado: $(sudo wg show | grep -c handshake) handshake(s)"

# ─── 5. Configurar VXLAN sobre WG ──────────────────────────────────────────
echo ""
echo "🔗 Configurando VXLAN sobre WireGuard..."
sudo ip link delete vxlan0 2>/dev/null || true
sudo ip link add vxlan0 type vxlan id $VXLAN_ID \
    remote ${WG_SUBNET}.$([ "$NODE_NUM" = "1" ] && echo "1" || echo "2") \
    dstport 8472 dev wg0
sudo ip link set vxlan0 up
echo "   vxlan0 creado (VNI $VXLAN_ID)"

# ─── 6. Configurar batman-adv sobre VXLAN ──────────────────────────────────
echo ""
echo "🦇 Configurando batman-adv..."
if lsmod | grep -q batman_adv 2>/dev/null; then
    sudo modprobe batman-adv 2>/dev/null || true
fi
sudo batctl if add vxlan0 2>/dev/null || true
sudo ip link set bat0 up
sudo ip addr flush dev bat0 2>/dev/null || true
sudo ip addr add ${MESH_IP}/24 dev bat0
echo "   bat0 con IP $MESH_IP/24"

# ─── 7. Verificar ──────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════"
echo "  📊 Estado de la mesh"
echo "═══════════════════════════════════════════════"
sudo wg show 2>/dev/null | head -10
echo ""
echo "Interfaces batman-adv:"
batctl if 2>/dev/null || echo "   (sin interfaz)"
echo ""
echo "Vecinos:"
batctl n 2>/dev/null || echo "   (sin vecinos aún)"
echo ""
echo "Ping al otro nodo:"
ping -c 2 -W 3 ${MESH_SUBNET}.$([ "$NODE_NUM" = "1" ] && echo "12" || echo "11") 2>&1 | tail -2 || echo "   (esperar discovery...)"
echo ""
echo "✅ Setup completo en $NODE_NAME"
