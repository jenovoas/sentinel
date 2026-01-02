#!/bin/bash
# Sentinel Dashboard Health Check Script
# Run this to verify everything is working

set -e

echo "🔍 Sentinel Dashboard Health Check"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_container() {
  local name=$1
  if docker-compose ps | grep -q "$name.*Up"; then
    echo -e "${GREEN}✅${NC} $name: Running"
    return 0
  else
    echo -e "${RED}❌${NC} $name: Not running"
    return 1
  fi
}

check_endpoint() {
  local url=$1
  local expected_code=${2:-200}
  local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  
  if [ "$response" = "$expected_code" ]; then
    echo -e "${GREEN}✅${NC} $url: $response"
    return 0
  else
    echo -e "${RED}❌${NC} $url: $response (expected $expected_code)"
    return 1
  fi
}

echo "1️⃣  Container Status"
echo "-------------------"
check_container "sentinel-postgres"
check_container "sentinel-redis"
check_container "sentinel-backend"
check_container "sentinel-frontend"
check_container "sentinel-nginx"
echo ""

echo "2️⃣  API Endpoints"
echo "----------------"
check_endpoint "http://localhost:8000/api/v1/health" 200
check_endpoint "http://localhost:8000/api/v1/dashboard/status" 200
echo ""

echo "3️⃣  Frontend"
echo "------------"
if curl -s http://localhost:3000/dash-op 2>/dev/null | grep -q "Operational Dashboard"; then
  echo -e "${GREEN}✅${NC} Dashboard UI: Loading correctly"
else
  echo -e "${YELLOW}⚠️${NC}  Dashboard UI: Loading (may be compiling)"
fi
echo ""

echo "4️⃣  System Health"
echo "----------------"
HEALTH=$(curl -s http://localhost:8000/api/v1/health 2>/dev/null)
DB_STATUS=$(echo $HEALTH | jq -r '.components.database.status' 2>/dev/null || echo "unknown")
REDIS_STATUS=$(echo $HEALTH | jq -r '.components.redis.status' 2>/dev/null || echo "unknown")
OLLAMA_STATUS=$(echo $HEALTH | jq -r '.components.ollama.status' 2>/dev/null || echo "unknown")

[ "$DB_STATUS" = "healthy" ] && echo -e "${GREEN}✅${NC} Database: OK" || echo -e "${RED}❌${NC} Database: FAILED ($DB_STATUS)"
[ "$REDIS_STATUS" = "healthy" ] && echo -e "${GREEN}✅${NC} Redis: OK" || echo -e "${RED}❌${NC} Redis: FAILED ($REDIS_STATUS)"
[ "$OLLAMA_STATUS" = "healthy" ] && echo -e "${GREEN}✅${NC} Ollama AI: OK" || echo -e "${YELLOW}⚠️${NC}  Ollama AI: DISABLED ($OLLAMA_STATUS)"
echo ""

echo "5️⃣  Dashboard Metrics"
echo "--------------------"
METRICS=$(curl -s http://localhost:8000/api/v1/dashboard/status 2>/dev/null)
CPU=$(echo $METRICS | jq -r '.system.cpu_percent' 2>/dev/null || echo "N/A")
MEM=$(echo $METRICS | jq -r '.system.mem_percent' 2>/dev/null || echo "N/A")
DB_CONN=$(echo $METRICS | jq -r '.db_stats.connections_total' 2>/dev/null || echo "N/A")

echo "CPU Usage: ${CPU}%"
echo "Memory Usage: ${MEM}%"
echo "DB Connections: ${DB_CONN}"
echo ""

echo "=================================="
echo "✅ Health check complete!"
echo ""
echo "🌐 Dashboard: http://localhost:3000/dash-op"
echo "📊 API: http://localhost:8000/api/v1/health"
