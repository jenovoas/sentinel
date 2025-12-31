#!/bin/bash
# EEVDF Stress Test - Validate latency under load
# Target: <20μs average latency under CPU/IO stress

set -e

echo "========================================="
echo "EEVDF Stress Test - Guardian-Alpha"
echo "Target: <20μs under load"
echo "========================================="
echo ""

# Start stress in background
echo "Starting stress (4 CPU, 2 IO, 1 VM)..."
stress-ng --cpu 4 --io 2 --vm 1 --vm-bytes 512M --timeout 60s &
STRESS_PID=$!

# Wait for stress to ramp up
sleep 3

echo "Running latency measurement under load (30s)..."
sudo timeout 30s bpftrace /home/jnovoas/sentinel/scripts/measure_guardian_latency.bt 2>&1 | tee /tmp/eevdf_stress_results.txt

# Wait for stress to finish
wait $STRESS_PID 2>/dev/null || true

echo ""
echo "========================================="
echo "Stress Test Complete"
echo "========================================="
echo ""
echo "Results saved to: /tmp/eevdf_stress_results.txt"
