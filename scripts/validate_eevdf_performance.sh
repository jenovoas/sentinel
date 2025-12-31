#!/bin/bash
# Complete EEVDF Performance Validation
# Uses bpftrace for precise LSM hook latency measurement

set -e

echo "========================================="
echo "Sentinel Cortex™ - EEVDF Validation"
echo "Kernel: $(uname -r)"
echo "========================================="
echo ""

# Check tools
if ! command -v bpftrace &> /dev/null; then
    echo "ERROR: bpftrace not installed"
    exit 1
fi

if ! /usr/sbin/bpftool version &> /dev/null; then
    echo "ERROR: bpftool not found at /usr/sbin/bpftool"
    exit 1
fi

echo "✓ bpftrace: $(bpftrace --version | head -1)"
echo "✓ bpftool: $(/usr/sbin/bpftool version | head -1)"
echo ""

# Show current eBPF programs
echo "Current eBPF Programs:"
echo "---------------------"
sudo /usr/sbin/bpftool prog list | head -10 || echo "No eBPF programs loaded"
echo ""

# Run latency measurement
echo "Starting LSM Hook Latency Measurement..."
echo "Duration: 30 seconds"
echo "Target: <100μs average latency"
echo ""
echo "Generating test events in background..."

# Generate events in background
(
    sleep 2
    for i in {1..50}; do
        ls /bin/* > /dev/null 2>&1
        sleep 0.5
    done
) &

# Run bpftrace measurement
sudo timeout 30s bpftrace /home/jnovoas/sentinel/scripts/measure_guardian_latency.bt 2>&1 || true

echo ""
echo "========================================="
echo "Validation Complete"
echo "========================================="
