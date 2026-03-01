#!/bin/bash
# Sentinel - Start All Containers with WireGuard Network
# Inicia todos los servicios conectados a la red WireGuard

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

cd ~/Dev/sentinel

echo "🚀 Iniciando Stack Completo de Sentinel"
echo "========================================"
echo ""

# 1. Iniciar servicios base (PostgreSQL, Redis)
echo -e "${YELLOW}[1/6] Iniciando servicios base...${NC}"
sudo podman-compose up -d postgres redis
sleep 5
echo -e "${GREEN}✓${NC} Servicios base iniciados"

# 2. Esperar PostgreSQL
echo -e "${YELLOW}[2/6] Esperando PostgreSQL...${NC}"
until sudo podman exec sentinel-postgres pg_isready -U sentinel_user > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✓${NC} PostgreSQL listo"

# 3. Esperar Redis
echo -e "${YELLOW}[3/6] Esperando Redis...${NC}"
until sudo podman exec sentinel-redis redis-cli ping > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e "${GREEN}✓${NC} Redis listo"

# 4. Iniciar backend y workers
echo -e "${YELLOW}[4/6] Iniciando backend y workers...${NC}"
sudo podman-compose up -d backend celery_worker celery_beat
sleep 10
echo -e "${GREEN}✓${NC} Backend iniciado"

# 5. Iniciar observabilidad
echo -e "${YELLOW}[5/6] Iniciando stack de observabilidad...${NC}"
sudo podman-compose up -d prometheus loki promtail grafana node-exporter postgres-exporter redis-exporter
sleep 15
echo -e "${GREEN}✓${NC} Observabilidad iniciada"

# 6. Iniciar servicios adicionales
echo -e "${YELLOW}[6/6] Iniciando servicios adicionales...${NC}"
sudo podman-compose up -d n8n nginx frontend
sleep 10
echo -e "${GREEN}✓${NC} Servicios adicionales iniciados"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Stack completo iniciado!"
echo ""
echo "📊 Accede a:"
echo ""
echo "  • Grafana:       http://localhost:3001"
echo "    Usuario:       admin"
echo "    Password:      $GRAFANA_PASSWORD"
echo ""
echo "  • Prometheus:    http://localhost:9090"
echo "  • Loki:          http://localhost:3100"
echo "  • n8n:           http://localhost:5678"
echo "  • Backend API:   http://localhost:8000"
echo "  • Frontend:      http://localhost:3000"
echo ""
echo "🔗 Red WireGuard: sentinel-wg (10.89.0.0/24)"
echo ""
echo "⚙️  Para detener: sudo podman-compose down"
echo ""

# Verificación final
echo "🔍 Verificando servicios..."
sleep 5

services=("prometheus:9090" "grafana:3001" "loki:3100" "node-exporter:9100" "backend:8000")
for service in "${services[@]}"; do
    name="${service%%:*}"
    port="${service##*:}"
    if curl -s --connect-timeout 2 http://localhost:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name (puerto $port) responding"
    else
        echo -e "${RED}✗${NC} $name (puerto $port) no responde"
    fi
done

echo ""
echo "✅ Proceso completado"
