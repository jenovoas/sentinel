#!/bin/bash
# Validation script - Test each claim with real data

echo "=== TIMESTAMP EXTRACTION TEST ==="
echo ""

# Get a real trace line
echo "1. Getting real trace line..."
LINE=$(sudo cat /sys/kernel/debug/tracing/trace 2>/dev/null | grep QUANTUM | tail -1)

if [ -z "$LINE" ]; then
    echo "No QUANTUM events found. Generate one first:"
    echo "  /bin/echo test"
    exit 1
fi

echo "Real line:"
echo "$LINE"
echo ""

# Test regex extraction
echo "2. Testing regex: r'\s+(\d+\.\d+):\s+'"
TIMESTAMP=$(echo "$LINE" | grep -oP '\s+\K\d+\.\d+(?=:\s+)')
echo "Extracted timestamp: $TIMESTAMP"
echo ""

# Get system uptime
echo "3. System uptime:"
UPTIME=$(cat /proc/uptime | awk '{print $1}')
echo "/proc/uptime: $UPTIME"
echo ""

# Get CLOCK_MONOTONIC
echo "4. CLOCK_MONOTONIC (Python):"
python3 << 'EOF'
import time
print(f"time.clock_gettime(CLOCK_MONOTONIC): {time.clock_gettime(time.CLOCK_MONOTONIC):.6f}")
EOF
echo ""

# Calculate lag
echo "5. Lag calculation:"
if [ -n "$TIMESTAMP" ]; then
    LAG=$(python3 -c "print(f'{$UPTIME - $TIMESTAMP:.6f}')")
    echo "Lag (uptime - timestamp): $LAG seconds"
    
    if (( $(echo "$LAG < 0" | bc -l) )); then
        echo "⚠️  NEGATIVE LAG - Clock mismatch!"
    elif (( $(echo "$LAG > 10" | bc -l) )); then
        echo "⚠️  LAG > 10s - Possible issue"
    else
        echo "✅ Lag looks reasonable"
    fi
else
    echo "❌ Failed to extract timestamp"
fi
echo ""

# Check trace clock
echo "6. Trace clock type:"
CLOCK=$(cat /sys/kernel/debug/tracing/trace_clock 2>/dev/null)
if [ -n "$CLOCK" ]; then
    echo "$CLOCK"
    echo ""
    if echo "$CLOCK" | grep -q "\[local\]"; then
        echo "✅ Using 'local' clock (CLOCK_MONOTONIC per-CPU)"
    elif echo "$CLOCK" | grep -q "\[global\]"; then
        echo "⚠️  Using 'global' clock (may differ from uptime)"
    fi
else
    echo "❌ Cannot read trace_clock (permission denied)"
fi
echo ""

# Full format breakdown
echo "7. Format breakdown:"
echo "$LINE" | sed 's/\(.*\)-\([0-9]*\)  \[\([0-9]*\)\] \(.*\) \([0-9.]*\):\(.*\)/Command: \1\nPID: \2\nCPU: \3\nFlags: \4\nTimestamp: \5\nRest: \6/'
