#!/bin/bash

# ============================================
# STAGING DEPLOYMENT SCRIPT
# For INTERNAL TESTING ONLY
# ============================================

set -e  # Exit on error

echo "🧪 Deploying Sentinel Cortex - STAGING (Internal Testing)"
echo "=========================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"

# Load environment
if [ ! -f .env.staging ]; then
    echo -e "${RED}❌ .env.staging not found${NC}"
    exit 1
fi

source .env.staging
echo -e "${GREEN}✅ Environment loaded${NC}"

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p nginx/ssl
mkdir -p backend/logs
mkdir -p monitoring
echo -e "${GREEN}✅ Directories created${NC}"

# Generate self-signed SSL (for local testing)
if [ ! -f nginx/ssl/staging.crt ]; then
    echo -e "${YELLOW}Generating self-signed SSL certificate...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/staging.key \
        -out nginx/ssl/staging.crt \
        -subj "/C=CL/ST=BioBio/L=Curanilahue/O=Sentinel/CN=staging.local"
    echo -e "${GREEN}✅ SSL certificate generated${NC}"
fi

# Pull latest images
echo -e "${YELLOW}Pulling Docker images...${NC}"
docker-compose -f docker-compose.staging.yml pull
echo -e "${GREEN}✅ Images pulled${NC}"

# Stop existing staging (if any)
echo -e "${YELLOW}Stopping existing staging environment...${NC}"
docker-compose -f docker-compose.staging.yml down 2>/dev/null || true
echo -e "${GREEN}✅ Stopped${NC}"

# Start staging
echo -e "${YELLOW}Starting staging environment...${NC}"
docker-compose -f docker-compose.staging.yml up -d
echo -e "${GREEN}✅ Services started${NC}"

# Wait for services
echo -e "${YELLOW}Waiting for services to be healthy (60s)...${NC}"
sleep 60

# Health checks
echo -e "${YELLOW}Running health checks...${NC}"

check_service() {
    local service=$1
    local url=$2
    local expected=$3
    
    echo -n "  Checking $service... "
    
    response=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

check_service "Backend" "http://localhost:8000/health" "200"
check_service "Grafana" "http://localhost:3000/api/health" "200"
check_service "Prometheus" "http://localhost:9090/-/healthy" "200"
check_service "Loki" "http://localhost:3101/ready" "200"

# Show services
echo ""
echo -e "${GREEN}=========================================================="
echo "✅ STAGING ENVIRONMENT DEPLOYED"
echo "==========================================================${NC}"
echo ""
echo "📊 Access URLs (INTERNAL ONLY):"
echo "  - Grafana:    http://localhost:3000 (admin/staging_admin_change_me)"
echo "  - Backend:    http://localhost:8000"
echo "  - Prometheus: http://localhost:9090"
echo "  - Loki:       http://localhost:3101"
echo "  - n8n:        http://localhost:5678 (admin/staging_n8n_password)"
echo ""
echo "🧪 Next Steps:"
echo "  1. Run tests: ./scripts/test-staging.sh"
echo "  2. Run benchmarks: cd backend && python benchmark_dual_lane.py"
echo "  3. Run fuzzer: cd backend && python fuzzer_aiopsdoom.py"
echo ""
echo "📋 View logs: docker-compose -f docker-compose.staging.yml logs -f"
echo "🛑 Stop: docker-compose -f docker-compose.staging.yml down"
echo ""
echo -e "${YELLOW}⚠️  INTERNAL TESTING ONLY - NOT FOR PUBLIC ACCESS${NC}"
