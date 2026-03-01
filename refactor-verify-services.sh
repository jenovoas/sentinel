#!/bin/bash
# Sentinel - Verify All Services
# Verifica que todos los servicios estén corriendo correctamente

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Verificando Servicios de Sentinel"
echo "====================================="
echo ""

# 1. Contenedores Podman
echo -e "${YELLOW}[1/5] Contenedores Podman...${NC}"
sudo podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|sentinel"
echo ""

# 2. Puertos críticos
echo -e "${YELLOW}[2/5] Puertos críticos...${NC}"
CRITICAL_PORTS="3000 3001 8000 5432 6379 9090 9100 3100 5678"
for port in $CRITICAL_PORTS; do
    if sudo netstat -tulpn | grep -q ":$port"; then
        service=$(sudo netstat -tulpn | grep ":$port" | awk '{print $7}' | cut -d'/' -f2)
        echo -e "${GREEN}✓${NC} Puerto $port (${service:-unknown})"
    else
        echo -e "${RED}✗${NC} Puerto $port NO está escuchando"
    fi
done
echo ""

# 3. Salud de servicios HTTP
echo -e "${YELLOW}[3/5] Salud de servicios HTTP...${NC}"
declare -A health_checks=(
    ["Grafana"]="http://localhost:3001/api/health"
    ["Prometheus"]="http://localhost:9090/-/healthy"
    ["Loki"]="http://localhost:3100/ready"
    ["Node Exporter"]="http://localhost:9100/metrics"
    ["Backend"]="http://localhost:8000/api/v1/health"
)

for service in "${!health_checks[@]}"; do
    url="${health_checks[$service]}"
    if curl -s --connect-timeout 3 "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service"
    else
        echo -e "${RED}✗${NC} $service"
    fi
done
echo ""

# 4. Servicios systemd
echo -e "${YELLOW}[4/5] Servicios systemd...${NC}"
SYSTEMD_SERVICES="samba-ad-dc pdns chrony sshd"
for service in $SYSTEMD_SERVICES; do
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓${NC} $service"
    else
        echo -e "${RED}✗${NC} $service"
    fi
done
echo ""

# 5. WireGuard
echo -e "${YELLOW}[5/5] WireGuard...${NC}"
if sudo wg show | grep -q "latest handshake"; then
    last_handshake=$(sudo wg show | grep "latest handshake" | awk -F'ago' '{print $1}' | tail -1)
    echo -e "${GREEN}✓${NC} WireGuard activo (último handshake: $last_handshake ago)"
else
    echo -e "${RED}✗${NC} WireGuard sin handshakes recientes"
fi
echo ""

# Resumen
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Contar errores
errors=0
for port in $CRITICAL_PORTS; do
    if ! sudo netstat -tulpn | grep -q ":$port"; then
        ((errors++))
    fi
done

for service in "${!health_checks[@]}"; do
    if ! curl -s --connect-timeout 3 "${health_checks[$service]}" > /dev/null 2>&1; then
        ((errors++))
    fi
done

if [ $errors -eq 0 ]; then
    echo -e "${GREEN}✅ Todos los servicios están operativos${NC}"
    exit 0
else
    echo -e "${RED}❌ $errors servicio(s) con problemas${NC}"
    exit 1
fi
