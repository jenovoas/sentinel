#!/bin/bash
# Dual-Lane Stress Test
# Validates Security Lane independence under Observability Lane saturation

set -e

echo "========================================="
echo "Dual-Lane Stress Test"
echo "Validating Security Lane Independence"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKEND_URL="http://localhost:8000"
OPS_EVENTS_PER_SEC=1000
SECURITY_EVENTS=10
TEST_DURATION=60

echo "Test Configuration:"
echo "  - Observability Lane: ${OPS_EVENTS_PER_SEC} events/sec"
echo "  - Security Lane: ${SECURITY_EVENTS} critical events"
echo "  - Duration: ${TEST_DURATION} seconds"
echo "  - Target: Security latency <10ms (independent of ops load)"
echo ""

# Check if backend is running
if ! curl -s -f "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}ERROR:${NC} Backend not running at ${BACKEND_URL}"
    echo "Start with: docker-compose up -d backend"
    exit 1
fi

echo "1. Baseline: Security Lane (No Load)"
echo "-------------------------------------"

# Measure baseline latency
BASELINE_START=$(date +%s%3N)
for i in $(seq 1 ${SECURITY_EVENTS}); do
    curl -s -X POST "${BACKEND_URL}/api/security/lane/emit" \
        -H "Content-Type: application/json" \
        -d "{\"source\":\"ebpf\",\"priority\":\"critical\",\"data\":{\"test\":\"baseline\",\"event\":${i}}}" \
        > /dev/null
done
BASELINE_END=$(date +%s%3N)
BASELINE_LATENCY=$(( (BASELINE_END - BASELINE_START) / SECURITY_EVENTS ))

echo -e "${GREEN}✓${NC} Baseline latency: ${BASELINE_LATENCY}ms per event"
echo ""

echo "2. Stress Test: Saturate Observability Lane"
echo "--------------------------------------------"

# Start observability lane saturation in background
echo "Starting observability saturation (${OPS_EVENTS_PER_SEC} events/sec)..."

python3 << EOF &
import requests
import time
import json

url = "${BACKEND_URL}/api/observability/lane/emit"
events_per_sec = ${OPS_EVENTS_PER_SEC}
duration = ${TEST_DURATION}

start_time = time.time()
event_count = 0

while time.time() - start_time < duration:
    batch_start = time.time()
    
    # Send batch of events
    for i in range(events_per_sec):
        try:
            requests.post(url, json={
                "source": "prometheus",
                "priority": "low",
                "data": {
                    "metric": "cpu_usage",
                    "value": 50 + (event_count % 50),
                    "timestamp": time.time()
                }
            }, timeout=0.1)
            event_count += 1
        except:
            pass  # Ignore errors during saturation
    
    # Sleep to maintain rate
    elapsed = time.time() - batch_start
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

print(f"Observability saturation complete: {event_count} events sent")
EOF

OPS_PID=$!
echo "Observability saturation started (PID: ${OPS_PID})"

# Wait for saturation to ramp up
sleep 5

echo ""
echo "3. Inject Security Events During Saturation"
echo "--------------------------------------------"

# Measure security lane latency under load
STRESS_START=$(date +%s%3N)
STRESS_LATENCIES=()

for i in $(seq 1 ${SECURITY_EVENTS}); do
    EVENT_START=$(date +%s%3N)
    
    curl -s -X POST "${BACKEND_URL}/api/security/lane/emit" \
        -H "Content-Type: application/json" \
        -d "{\"source\":\"ebpf\",\"priority\":\"critical\",\"data\":{\"test\":\"stress\",\"event\":${i},\"threat\":\"malware\"}}" \
        > /dev/null
    
    EVENT_END=$(date +%s%3N)
    EVENT_LATENCY=$((EVENT_END - EVENT_START))
    STRESS_LATENCIES+=($EVENT_LATENCY)
    
    echo "  Event ${i}: ${EVENT_LATENCY}ms"
    
    # Small delay between security events
    sleep 1
done

STRESS_END=$(date +%s%3N)
STRESS_AVG_LATENCY=$(( (STRESS_END - STRESS_START) / SECURITY_EVENTS ))

# Stop observability saturation
kill $OPS_PID 2>/dev/null || true
wait $OPS_PID 2>/dev/null || true

echo ""
echo "4. Results Analysis"
echo "-------------------"

# Calculate max latency
MAX_LATENCY=0
for latency in "${STRESS_LATENCIES[@]}"; do
    if [ $latency -gt $MAX_LATENCY ]; then
        MAX_LATENCY=$latency
    fi
done

echo "Baseline (no load):"
echo "  Average: ${BASELINE_LATENCY}ms"
echo ""
echo "Under Load (${OPS_EVENTS_PER_SEC} ops events/sec):"
echo "  Average: ${STRESS_AVG_LATENCY}ms"
echo "  Maximum: ${MAX_LATENCY}ms"
echo ""

# Calculate degradation
DEGRADATION=$(( ((STRESS_AVG_LATENCY - BASELINE_LATENCY) * 100) / BASELINE_LATENCY ))

echo "Performance Impact:"
echo "  Degradation: ${DEGRADATION}%"
echo ""

# Validate results
PASSED=true

if [ $STRESS_AVG_LATENCY -gt 10 ]; then
    echo -e "${RED}✗ FAILED:${NC} Average latency ${STRESS_AVG_LATENCY}ms > 10ms target"
    PASSED=false
else
    echo -e "${GREEN}✓ PASSED:${NC} Average latency ${STRESS_AVG_LATENCY}ms < 10ms target"
fi

if [ $MAX_LATENCY -gt 20 ]; then
    echo -e "${RED}✗ FAILED:${NC} Max latency ${MAX_LATENCY}ms > 20ms acceptable"
    PASSED=false
else
    echo -e "${GREEN}✓ PASSED:${NC} Max latency ${MAX_LATENCY}ms < 20ms acceptable"
fi

if [ $DEGRADATION -gt 50 ]; then
    echo -e "${YELLOW}⚠ WARNING:${NC} Degradation ${DEGRADATION}% > 50%"
else
    echo -e "${GREEN}✓ PASSED:${NC} Degradation ${DEGRADATION}% < 50%"
fi

echo ""
echo "========================================="
if [ "$PASSED" = true ]; then
    echo -e "${GREEN}TEST PASSED${NC}"
    echo "Security Lane is INDEPENDENT of Observability Lane load"
else
    echo -e "${RED}TEST FAILED${NC}"
    echo "Security Lane is AFFECTED by Observability Lane load"
fi
echo "========================================="

exit 0
