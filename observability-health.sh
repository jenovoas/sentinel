#!/bin/bash
# Health Check del Stack de Observabilidad

echo "🏥 Health Check - Stack de Observabilidad"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Prometheus
echo -n "Checking Prometheus... "
if curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓ UP${NC}"
    
    # Check targets
    TARGETS_UP=$(curl -s http://localhost:9090/api/v1/targets 2>/dev/null | jq -r '.data.activeTargets[] | select(.health=="up") | .labels.job' 2>/dev/null | wc -l)
    echo "  └─ Targets UP: $TARGETS_UP"
else
    echo -e "${RED}✗ DOWN${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Loki
echo -n "Checking Loki... "
if curl -sf http://localhost:3100/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✓ UP${NC}"
else
    echo -e "${YELLOW}⚠ STARTING${NC} (puede tardar 30s)"
fi

# Promtail
echo -n "Checking Promtail... "
if curl -sf http://localhost:9080/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✓ UP${NC}"
else
    echo -e "${YELLOW}⚠ STARTING${NC}"
fi

# Node Exporter
echo -n "Checking Node Exporter... "
if curl -sf http://localhost:9100/metrics | head -1 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ UP${NC}"
    
    # Check metrics count
    METRICS=$(curl -s http://localhost:9100/metrics 2>/dev/null | grep -c "^node_")
    echo "  └─ Metrics available: $METRICS"
else
    echo -e "${RED}✗ DOWN${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Grafana
echo -n "Checking Grafana... "
if curl -sf http://localhost:3001/api/health > /dev/null 2>&1; then
    VERSION=$(curl -s http://localhost:3001/api/health 2>/dev/null | jq -r '.version' 2>/dev/null)
    echo -e "${GREEN}✓ UP${NC} (v$VERSION)"
    
    # Check datasources
    echo "  └─ Datasources:"
    echo "     • Prometheus: http://prometheus:9090"
    echo "     • Loki: http://loki:3100"
else
    echo -e "${YELLOW}⚠ STARTING${NC} (puede tardar 15s)"
fi

echo ""
echo "🌐 URLs:"
echo "  • Grafana:       http://localhost:3001"
echo "  • Prometheus:    http://localhost:9090"
echo "  • Node Exporter: http://localhost:9100/metrics"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All critical services are UP${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS service(s) DOWN${NC}"
    echo ""
    echo "Run: docker-compose logs <service>"
    exit 1
fi
