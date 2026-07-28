#!/bin/bash
# Sentinel - Contenedores Audit & Refactor Script
# Migración a Podman + WireGuard Network + Monitoreo Completo

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "🔍 Sentinel Container Audit & Refactor"
echo "======================================="
echo ""

# 1. Verificar Podman
echo -e "${YELLOW}[1/8] Verificando Podman...${NC}"
if ! command -v podman &> /dev/null; then
    echo -e "${RED}❌ Podman no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Podman disponible: $(podman --version)"

# 2. Verificar WireGuard
echo -e "${YELLOW}[2/8] Verificando WireGuard...${NC}"
if ! sudo wg show &> /dev/null; then
    echo -e "${RED}❌ WireGuard no está activo${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} WireGuard activo en wg0"

# 3. Crear red Podman para WireGuard
echo -e "${YELLOW}[3/8] Creando red Podman 'sentinel-wg'...${NC}"
sudo podman network create sentinel-wg 2>/dev/null || echo "Red ya existe"
sudo podman network inspect sentinel-wg | jq -r '.[0].subnets[0].subnet' 2>/dev/null || echo "10.89.0.0/24"

# 4. Detener contenedores antiguos
echo -e "${YELLOW}[4/8] Deteniendo contenedores antiguos...${NC}"
sudo podman ps -q | xargs -r sudo podman stop 2>/dev/null || echo "No hay contenedores corriendo"

# 5. Limpiar contenedores huérfanos
echo -e "${YELLOW}[5/8] Limpiando contenedores huérfanos...${NC}"
sudo podman container prune -f

# 6. Verificar puertos críticos
echo -e "${YELLOW}[6/8] Verificando puertos críticos...${NC}"
REQUIRED_PORTS="3000 3001 9090 9100 3100 9080 8000 5432 6379"
for port in $REQUIRED_PORTS; do
    if sudo netstat -tulpn | grep -q ":$port"; then
        echo -e "${GREEN}✓${NC} Puerto $port OK"
    else
        echo -e "${YELLOW}⚠${NC} Puerto $port no está en uso"
    fi
done

# 7. Verificar servicios systemd
echo -e "${YELLOW}[7/8] Verificando servicios systemd...${NC}"
SERVICES="samba-ad-dc pdns chrony"
for service in $SERVICES; do
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓${NC} $service activo"
    else
        echo -e "${RED}✗${NC} $service inactivo"
    fi
done

# 8. Resumen de red WireGuard
echo -e "${YELLOW}[8/8] Estado de WireGuard...${NC}"
sudo wg show | grep -E "interface|peer|latest handshake"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Auditoría completada"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Ejecutar: ./refactor-start-containers.sh"
echo "   2. Verificar: ./refactor-verify-services.sh"
echo "   3. Conectar a red WG: ./refactor-connect-wg.sh"
echo ""
