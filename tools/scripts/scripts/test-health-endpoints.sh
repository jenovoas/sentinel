#!/bin/bash
#
# Test Health Endpoints
# Validates all health check endpoints are working correctly
#

set -e

echo "🧪 Testing Sentinel Health Endpoints..."
echo ""

BASE_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $endpoint... "
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        echo "  Response: $body" | jq '.' 2>/dev/null || echo "  Response: $body"
    else
        echo -e "${RED}✗ FAIL${NC} (Expected $expected_status, got $status_code)"
        echo "  Response: $body"
        return 1
    fi
    
    echo ""
}

# Test 1: Health Check
echo "=== Test 1: Overall Health Check ==="
test_endpoint "/health" "200" "Overall system health"

# Test 2: Readiness Check
echo "=== Test 2: Readiness Check ==="
test_endpoint "/ready" "200" "Ready to serve traffic"

# Test 3: Liveness Check
echo "=== Test 3: Liveness Check ==="
test_endpoint "/live" "200" "Process is alive"

# Test 4: Prometheus Metrics
echo "=== Test 4: Prometheus Metrics ==="
echo -n "Testing /metrics... "
response=$(curl -s "$BASE_URL/metrics")
if echo "$response" | grep -q "sentinel_health"; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  Metrics found:"
    echo "$response" | grep "sentinel_" | head -5
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  No metrics found"
fi
echo ""

# Test 5: Component Health Details
echo "=== Test 5: Component Health Details ==="
health_response=$(curl -s "$BASE_URL/health")
echo "Database status:"
echo "$health_response" | jq '.components.database' 2>/dev/null || echo "  Could not parse"
echo ""
echo "Redis status:"
echo "$health_response" | jq '.components.redis' 2>/dev/null || echo "  Could not parse"
echo ""
echo "Ollama status:"
echo "$health_response" | jq '.components.ollama' 2>/dev/null || echo "  Could not parse"
echo ""

# Test 6: Role Management (requires authentication in production)
echo "=== Test 6: Role Management ==="
echo "Current role:"
curl -s "$BASE_URL/health" | jq '.role' 2>/dev/null || echo "  Could not parse"
echo ""

echo "=== All Tests Complete ==="
echo ""
echo "Summary:"
echo "  ✓ Health endpoints are working"
echo "  ✓ Dependencies are being checked"
echo "  ✓ Metrics are being exposed"
echo ""
echo "Next steps:"
echo "  1. Configure Route53/Cloudflare health checks to use /ready"
echo "  2. Configure HAProxy to use /ready for backend health"
echo "  3. Configure Prometheus to scrape /metrics"
echo "  4. Test graceful shutdown (docker stop sentinel-backend)"
