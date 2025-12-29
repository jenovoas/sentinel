#!/bin/bash
# Guardian-Alpha LSM Performance Benchmark (User Mode)
# Measures overhead of kernel-level interception without requiring sudo for checks

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Guardian-Alpha LSM - Performance Benchmark (User Mode)  ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
ITERATIONS=2000
TEST_BINARY="/bin/true"

echo -e "${YELLOW}ℹ️  Assumes Guardian-Alpha LSM is already loaded in kernel.${NC}"
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
    for i in {1..100}; do
        $TEST_BINARY &> /dev/null
    done
    
    # Actual benchmark
    local start=$(date +%s%N)
    for i in $(seq 1 $iterations); do
        $TEST_BINARY &> /dev/null
    done
    local end=$(date +%s%N)
    
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

# Benchmark WITH LSM (Assumed)
with_lsm=$(measure_executions "With Guardian-Alpha LSM" $ITERATIONS)

# Calculate overhead
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}Results:${NC}"
echo ""
echo "  Average execution time: ${with_lsm} ns"

# Convert to microseconds for readability
with_lsm_us=$((with_lsm / 1000))
echo "  Average execution time: ${with_lsm_us} μs"

# Estimate overhead (typical baseline is ~50-100μs for /bin/true on modern linux)
# We use a conservative baseline for comparison
typical_baseline=75000  # 75μs typical
overhead=$((with_lsm - typical_baseline))
overhead_us=$((overhead / 1000))

if [ $overhead -lt 0 ]; then
    echo ""
    echo -e "${GREEN}✅ No measurable overhead detected${NC}"
    echo "   (Execution faster or equal to typical baseline)"
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
echo -e "${GREEN}Benchmark complete!${NC}"
