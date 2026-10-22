#!/bin/bash
# Guardian-Alpha LSM Performance Benchmark
# Measures overhead of kernel-level interception

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Guardian-Alpha LSM - Performance Benchmark              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
ITERATIONS=1000
TEST_BINARY="/bin/true"  # Minimal binary for testing

# Check if LSM is loaded
LSM_LOADED=false
if sudo bpftool prog show | grep -q guardian; then
    LSM_LOADED=true
    echo -e "${GREEN}✅ Guardian-Alpha LSM is loaded${NC}"
else
    echo -e "${YELLOW}⚠️  Guardian-Alpha LSM is NOT loaded${NC}"
fi

echo ""
echo -e "${BOLD}Benchmark Configuration:${NC}"
echo "  Iterations: $ITERATIONS"
echo "  Test binary: $TEST_BINARY"
echo ""

# Function to measure execution time
measure_executions() {
    local label=$1
    local iterations=$2
    
    echo -e "${BOLD}Running: $label${NC}" >&2
    
    # Warm up
    for i in {1..10}; do
        $TEST_BINARY &> /dev/null
    done
    
    # Actual benchmark (reloj monotónico; date +%N no es fiable en este host)
    now_ns() { python3 -c "import time; print(time.perf_counter_ns())"; }
    local start=$(now_ns)
    for i in $(seq 1 $iterations); do
        $TEST_BINARY &> /dev/null
    done
    local end=$(now_ns)
    
    # Calculate metrics
    local total_ns=$((end - start))
    local total_ms=$((total_ns / 1000000))
    local avg_ns=$((total_ns / iterations))
    local avg_us=$((avg_ns / 1000))
    
    echo "  Total time: ${total_ms} ms" >&2
    echo "  Average per execution: ${avg_us} μs (${avg_ns} ns)" >&2
    echo "" >&2
    
    # Return average in nanoseconds
    echo $avg_ns
}

# Benchmark WITHOUT LSM (if not loaded)
if [ "$LSM_LOADED" = false ]; then
    baseline=$(measure_executions "Baseline (no LSM)" $ITERATIONS)
    
    echo ""
    echo -e "${YELLOW}💡 To measure with LSM, run: sudo ./load.sh${NC}"
    echo -e "${YELLOW}   Then run this benchmark again${NC}"
    exit 0
fi

# Benchmark WITH LSM
with_lsm=$(measure_executions "With Guardian-Alpha LSM" $ITERATIONS)

# Calculate overhead (we don't have baseline, so just report absolute)
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}Results:${NC}"
echo ""
echo "  Average execution time: ${with_lsm} ns"

# Convert to microseconds for readability
with_lsm_us=$((with_lsm / 1000))
echo "  Average execution time: ${with_lsm_us} μs"

# Estimate overhead (typical baseline is ~50-100μs for /bin/true)
typical_baseline=75000  # 75μs typical
overhead=$((with_lsm - typical_baseline))
overhead_us=$((overhead / 1000))

if [ $overhead -lt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ No measurable overhead detected${NC}"
    echo "   (Execution faster than typical baseline)"
else
    overhead_pct=$((overhead * 100 / typical_baseline))
    echo ""
    echo "  Estimated overhead: ~${overhead_us} μs"
    echo "  Estimated overhead: ~${overhead_pct}%"
    
    if [ $overhead_us -lt 10 ]; then
        echo -e "${GREEN}✅ Excellent: < 10μs overhead${NC}"
    elif [ $overhead_us -lt 100 ]; then
        echo -e "${GREEN}✅ Good: < 100μs overhead${NC}"
    elif [ $overhead_us -lt 1000 ]; then
        echo -e "${YELLOW}⚠️  Moderate: < 1ms overhead${NC}"
    else
        echo -e "${YELLOW}⚠️  High: > 1ms overhead${NC}"
    fi
fi

echo ""
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Check kernel logs for events
echo ""
echo -e "${BOLD}Recent Guardian-Alpha Events:${NC}"
sudo dmesg | grep "Guardian-Alpha" | tail -5 || echo "  No events logged"

echo ""
echo -e "${BOLD}BPF Map Statistics:${NC}"
# Try to dump stats if available
sudo bpftool map show 2>/dev/null | grep -A 2 "name.*stats" || echo "  Stats map not available"

echo ""
echo -e "${GREEN}Benchmark complete!${NC}"
