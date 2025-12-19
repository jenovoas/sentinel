#!/bin/bash
# Guardian-Alpha CPU Stress Test
# Chaos Engineering - Tier 1

echo "======================================"
echo "Chaos Test: Guardian-Alpha CPU Stress"
echo "======================================"
echo ""

# Configuration
DURATION=300  # 5 minutes
INTENSITY=90  # 90% CPU
CORES=4

echo "Configuration:"
echo "  Duration: ${DURATION}s"
echo "  Intensity: ${INTENSITY}%"
echo "  Cores: ${CORES}"
echo ""

# Check if Gremlin is installed
if ! command -v gremlin &> /dev/null; then
    echo "ERROR: Gremlin not installed"
    echo "Install: https://www.gremlin.com/docs/infrastructure-layer/installation/"
    exit 1
fi

# Run CPU stress attack
echo "Starting CPU stress attack on Guardian-Alpha..."
gremlin attack \
  --target "guardian-alpha-ebpf" \
  --type "cpu-stress" \
  --length ${DURATION} \
  --cores ${CORES} \
  --intensity ${INTENSITY}

# Monitor during test (in background)
echo ""
echo "Monitoring Guardian-Alpha during stress..."
for i in {1..30}; do
    echo "Check $i/30:"
    docker stats guardian-alpha --no-stream | tail -1
    
    # Check if syscall interception still works
    RESPONSE=$(curl -s -X POST http://localhost:8080/api/guardian/syscall-intercept \
        -H "Content-Type: application/json" \
        -d '{"syscall_nr": 59, "args": ["/bin/sh"], "pid": 1234}')
    
    if echo "$RESPONSE" | grep -q "decision"; then
        echo "  ✓ Syscall interception: WORKING"
    else
        echo "  ✗ Syscall interception: FAILED"
    fi
    
    sleep 10
done

echo ""
echo "======================================"
echo "CPU Stress Test Complete"
echo "======================================"
echo ""
echo "Expected Results:"
echo "  ✓ Guardian-Alpha continues intercepting syscalls"
echo "  ✓ Latency remains <1ms"
echo "  ✓ No syscall leaks"
echo ""
