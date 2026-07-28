#!/bin/bash
# Script de inicialización del Stack de Observabilidad
# Uso: ./observability-start.sh

set -e

echo "🚀 Iniciando Stack de Observabilidad de Sentinel..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker está disponible"

# Levantar servicios
echo ""
echo "📦 Iniciando servicios de observabilidad..."
docker-compose up -d prometheus loki promtail grafana node-exporter

# Esperar a que los servicios estén listos
echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar servicios
echo ""
echo "🔍 Verificando servicios..."

# Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Prometheus está corriendo (http://localhost:9090)"
else
    echo -e "${RED}✗${NC} Prometheus no responde"
fi

# Loki
if curl -s http://localhost:3100/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Loki está corriendo (http://localhost:3100)"
else
    echo -e "${YELLOW}⚠${NC} Loki está iniciando... (puede tardar unos segundos)"
fi

# Node Exporter
if curl -s http://localhost:9100/metrics | head -1 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Node Exporter está corriendo (http://localhost:9100)"
else
    echo -e "${RED}✗${NC} Node Exporter no responde"
fi

# Promtail
if curl -s http://localhost:9080/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Promtail está corriendo (http://localhost:9080)"
else
    echo -e "${YELLOW}⚠${NC} Promtail está iniciando..."
fi

# Grafana
if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Grafana está corriendo (http://localhost:3001)"
else
    echo -e "${YELLOW}⚠${NC} Grafana está iniciando... (puede tardar 10-15 segundos)"
fi

# Resumen
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Stack de Observabilidad iniciado!"
echo ""
echo "📊 Accede a:"
echo ""
echo "  • Grafana:       http://localhost:3001"
echo "    Usuario:       admin"
echo "    Password:      sentinel2024"
echo ""
echo "  • Prometheus:    http://localhost:9090"
echo "  • Loki:          http://localhost:3100"
echo "  • Node Exporter: http://localhost:9100/metrics"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 Dashboards pre-configurados en Grafana:"
echo "   - Sentinel - Host Metrics Overview"
echo "   - Sentinel - System Logs"
echo ""
echo "📚 Documentación: ./observability/README.md"
echo ""
echo "⚙️  Para detener: docker-compose down"
echo ""
