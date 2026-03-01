#!/bin/bash
# Sentinel - Connect Containers to WireGuard Network
# Conecta los contenedores a la red WireGuard para acceso remoto

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔗 Conectando Contenedores a WireGuard"
echo "======================================="
echo ""

# 1. Verificar red Podman existe
echo -e "${YELLOW}[1/4] Verificando red sentinel-wg...${NC}"
if ! sudo podman network inspect sentinel-wg &> /dev/null; then
    echo "Creando red sentinel-wg..."
    sudo podman network create --driver bridge --subnet 10.89.0.0/24 sentinel-wg
fi
echo -e "${GREEN}✓${NC} Red sentinel-wg disponible"

# 2. Conectar contenedores críticos
echo -e "${YELLOW}[2/4] Conectando contenedores a sentinel-wg...${NC}"
CONTAINERS="sentinel-postgres sentinel-redis sentinel-backend sentinel-grafana sentinel-prometheus"

for container in $CONTAINERS; do
    if sudo podman ps --format '{{.Names}}' | grep -q "^${container}$"; then
        sudo podman network connect sentinel-wg $container 2>/dev/null || echo "  $container: ya conectado o error"
        echo -e "${GREEN}✓${NC} $container conectado"
    else
        echo -e "${YELLOW}⚠${NC} $container no está corriendo"
    fi
done

# 3. Configurar rutas WireGuard
echo -e "${YELLOW}[3/4] Configurando rutas WireGuard...${NC}"
WG_INTERFACE="wg0"
WG_SUBNET="10.10.10.0/24"

# Permitir tráfico desde red WireGuard hacia contenedores
sudo iptables -A FORWARD -i $WG_INTERFACE -o podman+ -j ACCEPT 2>/dev/null || true
sudo iptables -A FORWARD -i podman+ -o $WG_INTERFACE -j ACCEPT 2>/dev/null || true

echo -e "${GREEN}✓${NC} Rutas configuradas"

# 4. Mostrar IPs asignadas
echo -e "${YELLOW}[4/4] IPs asignadas en red sentinel-wg...${NC}"
echo ""
echo "Contenedor                    IP en sentinel-wg"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for container in $CONTAINERS; do
    if sudo podman inspect $container &> /dev/null; then
        ip=$(sudo podman inspect $container --format '{{range .NetworkSettings.Networks}}{{if eq .NetworkID "sentinel-wg"}}{{.IPAddress}}{{end}}{{end}}' 2>/dev/null || echo "N/A")
        printf "%-30s %s\n" "$container" "$ip"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Contenedores conectados a WireGuard"
echo ""
echo "📊 Acceso desde otros nodos:"
echo ""
echo "  Desde kingu (10.10.10.1):"
echo "    curl http://10.89.0.X:3001  # Grafana"
echo "    curl http://10.89.0.X:9090  # Prometheus"
echo ""
echo "  Desde centurion (10.10.10.3):"
echo "    curl http://10.89.0.X:3001  # Grafana"
echo ""
echo "🔗 Para verificar conectividad:"
echo "   ping 10.89.0.X desde otros nodos WG"
echo ""
