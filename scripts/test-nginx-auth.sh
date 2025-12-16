#!/bin/bash
# Test Nginx Authentication
# Verifies that Prometheus and Loki require authentication

set -e

echo "🧪 Testing Nginx authentication for observability endpoints..."
echo ""

# Load credentials from .env
if [ -f .env ]; then
    source .env
else
    echo "⚠️  .env file not found, using defaults"
    OBSERVABILITY_METRICS_PASSWORD="changeme123"
    OBSERVABILITY_LOGS_PASSWORD="changeme456"
fi

METRICS_USER="sentinel_metrics"
LOGS_USER="sentinel_logs"

# Test 1: Prometheus without auth (should fail with 401)
echo "Test 1: Prometheus without authentication"
echo -n "  Querying http://localhost:9091/api/v1/query?query=up ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9091/api/v1/query?query=up 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ PASS (401 Unauthorized)"
else
    echo "❌ FAIL (got $HTTP_CODE, expected 401)"
    exit 1
fi

# Test 2: Prometheus with auth (should succeed with 200)
echo "Test 2: Prometheus with authentication"
echo -n "  Querying with credentials ... "
HTTP_CODE=$(curl -s -u "$METRICS_USER:$OBSERVABILITY_METRICS_PASSWORD" \
    -o /dev/null -w "%{http_code}" \
    http://localhost:9091/api/v1/query?query=up 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PASS (200 OK)"
else
    echo "❌ FAIL (got $HTTP_CODE, expected 200)"
    exit 1
fi

# Test 3: Loki read without auth (should fail with 401)
echo "Test 3: Loki read without authentication"
echo -n "  Querying http://localhost:3101/loki/api/v1/query ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    "http://localhost:3101/loki/api/v1/query?query={job=\"test\"}" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "401" ]; then
    echo "✅ PASS (401 Unauthorized)"
else
    echo "❌ FAIL (got $HTTP_CODE, expected 401)"
    exit 1
fi

# Test 4: Loki read with auth (should succeed with 200)
echo "Test 4: Loki read with authentication"
echo -n "  Querying with credentials ... "
HTTP_CODE=$(curl -s -u "$LOGS_USER:$OBSERVABILITY_LOGS_PASSWORD" \
    -o /dev/null -w "%{http_code}" \
    "http://localhost:3101/loki/api/v1/query?query={job=\"test\"}" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ PASS (200 OK)"
else
    echo "❌ FAIL (got $HTTP_CODE, expected 200)"
    exit 1
fi

echo ""
echo "🎉 All authentication tests passed!"
echo "   Observability endpoints are properly secured."
