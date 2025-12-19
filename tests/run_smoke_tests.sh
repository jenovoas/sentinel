#!/bin/bash
# Sentinel Smoke Tests - Quick validation of core functionality
# Safe to run on laptop, no heavy load

set -e

echo "======================================"
echo "Sentinel Smoke Tests"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SENTINEL_URL="${SENTINEL_URL:-http://localhost:8080}"
PASSED=0
FAILED=0

# Helper functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test 1: API Health Check
echo "Test 1: API Health Check"
if curl -s -f "${SENTINEL_URL}/health" > /dev/null; then
    pass "API is responding"
else
    fail "API is not responding"
fi
echo ""

# Test 2: Guardian-Alpha Status
echo "Test 2: Guardian-Alpha Status"
RESPONSE=$(curl -s "${SENTINEL_URL}/api/guardian/alpha/status")
if echo "$RESPONSE" | grep -q "active"; then
    pass "Guardian-Alpha is active"
else
    fail "Guardian-Alpha is not active"
fi
echo ""

# Test 3: Cortex AI Decision
echo "Test 3: Cortex AI Threat Detection"
RESPONSE=$(curl -s -X POST "${SENTINEL_URL}/api/cortex/threat-analysis" \
    -H "Content-Type: application/json" \
    -d '{"pattern": "DROP TABLE", "confidence_required": 0.9}')

if echo "$RESPONSE" | grep -q "threat_detected"; then
    pass "Cortex AI is responding"
    if echo "$RESPONSE" | grep -q '"threat_detected":true'; then
        pass "Threat correctly detected"
    else
        fail "Threat not detected"
    fi
else
    fail "Cortex AI not responding correctly"
fi
echo ""

# Test 4: Syscall Interception (simulated)
echo "Test 4: Syscall Interception Simulation"
RESPONSE=$(curl -s -X POST "${SENTINEL_URL}/api/guardian/syscall-intercept" \
    -H "Content-Type: application/json" \
    -d '{"syscall_nr": 59, "args": ["/bin/sh", "-c", "rm -rf /"], "pid": 1234}')

if echo "$RESPONSE" | grep -q "decision"; then
    pass "Guardian syscall endpoint responding"
    if echo "$RESPONSE" | grep -q '"decision":"BLOCK"'; then
        pass "Malicious syscall blocked"
    else
        fail "Malicious syscall not blocked"
    fi
else
    fail "Guardian syscall endpoint not responding"
fi
echo ""

# Test 5: Audit Log
echo "Test 5: Audit Log Persistence"
RESPONSE=$(curl -s -X POST "${SENTINEL_URL}/api/audit/log" \
    -H "Content-Type: application/json" \
    -d '{"action": "BLOCK", "reason": "Test", "timestamp": "'$(date -Iseconds)'"}')

if echo "$RESPONSE" | grep -q "audit_id"; then
    pass "Audit log persisted"
else
    fail "Audit log not persisted"
fi
echo ""

# Test 6: Database Connection
echo "Test 6: Database Connection"
RESPONSE=$(curl -s "${SENTINEL_URL}/api/db/status")
if echo "$RESPONSE" | grep -q "connected"; then
    pass "Database is connected"
else
    fail "Database connection failed"
fi
echo ""

# Test 7: Redis Connection
echo "Test 7: Redis Connection"
RESPONSE=$(curl -s "${SENTINEL_URL}/api/cache/status")
if echo "$RESPONSE" | grep -q "connected"; then
    pass "Redis is connected"
else
    fail "Redis connection failed"
fi
echo ""

# Summary
echo "======================================"
echo "Test Summary"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
