#!/bin/bash

# ============================================
# STAGING TEST SCRIPT
# Validates staging environment health
# ============================================

set -e

echo "🧪 Testing Sentinel Cortex - STAGING"
echo "====================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

FAILED=0
PASSED=0

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=$3
    local description=$4
    
    echo -n "Testing $name... "
    
    response=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} ($description)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_code, got $response)"
        ((FAILED++))
        return 1
    fi
}

# Test JSON response
test_json() {
    local name=$1
    local url=$2
    local jq_filter=$3
    local expected=$4
    
    echo -n "Testing $name... "
    
    response=$(curl -k -s "$url" 2>/dev/null | jq -r "$jq_filter" 2>/dev/null || echo "error")
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected '$expected', got '$response')"
        ((FAILED++))
        return 1
    fi
}

echo ""
echo -e "${YELLOW}1. SMOKE TESTS (Service Health)${NC}"
echo "--------------------------------"

test_endpoint "Backend Health" "http://localhost:8000/health" "200" "API responding"
test_endpoint "Grafana Health" "http://localhost:3000/api/health" "200" "Grafana up"
test_endpoint "Prometheus Health" "http://localhost:9090/-/healthy" "200" "Prometheus up"
test_endpoint "Loki Ready" "http://localhost:3101/ready" "200" "Loki ready"

test_json "Backend Status" "http://localhost:8000/health" ".status" "healthy"

echo ""
echo -e "${YELLOW}2. SECURITY TESTS${NC}"
echo "--------------------------------"

# Test unauthorized access
test_endpoint "Unauthorized Access" "http://localhost:8000/admin" "401" "Auth required"

# Test invalid HMAC (should be rejected)
echo -n "Testing HMAC validation... "
response=$(curl -k -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:3101/loki/api/v1/push \
    -H "Content-Type: application/json" \
    -H "X-Scope-OrgID: fake" \
    -H "X-Scope-Signature: invalid" \
    -d '{"streams": []}' 2>/dev/null || echo "000")

if [ "$response" = "401" ] || [ "$response" = "403" ]; then
    echo -e "${GREEN}✅ PASS${NC} (Invalid HMAC rejected)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Expected 401/403, got $response)"
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}3. PERFORMANCE TESTS${NC}"
echo "--------------------------------"

# Test response time
echo -n "Testing response time... "
start=$(date +%s%N)
curl -k -s http://localhost:8000/health > /dev/null 2>&1
end=$(date +%s%N)
duration=$(( (end - start) / 1000000 ))  # Convert to ms

if [ $duration -lt 100 ]; then
    echo -e "${GREEN}✅ PASS${NC} (${duration}ms < 100ms)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (${duration}ms >= 100ms)"
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}4. DATA INGESTION TESTS${NC}"
echo "--------------------------------"

# Test Loki ingestion
echo -n "Testing Loki ingestion... "
timestamp=$(date +%s%N)
response=$(curl -k -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:3101/loki/api/v1/push \
    -H "Content-Type: application/json" \
    -d "{\"streams\": [{\"stream\": {\"lane\": \"ops\", \"test\": \"true\"}, \"values\": [[\"$timestamp\", \"test log\"]]}]}" \
    2>/dev/null || echo "000")

if [ "$response" = "204" ]; then
    echo -e "${GREEN}✅ PASS${NC} (Log ingested)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Expected 204, got $response)"
    ((FAILED++))
fi

echo ""
echo -e "${YELLOW}5. INTEGRATION TESTS${NC}"
echo "--------------------------------"

# Check if services can communicate
echo -n "Testing service connectivity... "
docker-compose -f docker-compose.staging.yml exec -T backend \
    python -c "import requests; r = requests.get('http://loki:3100/ready'); exit(0 if r.status_code == 200 else 1)" \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} (Backend → Loki OK)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Backend → Loki FAILED)"
    ((FAILED++))
fi

echo ""
echo "====================================="
echo -e "${GREEN}PASSED: $PASSED${NC}"
echo -e "${RED}FAILED: $FAILED${NC}"
echo "====================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "🚀 Staging environment is healthy!"
    echo ""
    echo "Next steps:"
    echo "  - Run benchmarks: cd backend && python benchmark_dual_lane.py"
    echo "  - Run fuzzer: cd backend && python fuzzer_aiopsdoom.py"
    echo "  - Load test: ab -n 1000 -c 10 http://localhost:8000/health"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Check logs: docker-compose -f docker-compose.staging.yml logs"
    exit 1
fi
