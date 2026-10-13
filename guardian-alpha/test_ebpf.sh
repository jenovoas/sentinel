#!/bin/bash
# Simple test to verify eBPF is generating events

echo "=== Testing eBPF Event Generation ==="
echo ""

# Check if program is loaded
echo "1. Checking if eBPF program is loaded..."
PROG_ID=$(sudo bpftool prog list | grep quantum_bprm_check | awk '{print $1}' | tr -d ':')
if [ -z "$PROG_ID" ]; then
    echo "❌ No quantum program found!"
    exit 1
fi
echo "✅ Program ID: $PROG_ID"

# Check if link exists
echo ""
echo "2. Checking if LSM link is attached..."
sudo bpftool link list | grep "prog $PROG_ID" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Link is attached"
else
    echo "❌ No link found!"
    exit 1
fi

# Clear trace buffer
echo ""
echo "3. Clearing trace buffer..."
sudo sh -c "echo > /sys/kernel/debug/tracing/trace"

# Generate an event
echo ""
echo "4. Generating test event..."
/bin/echo "test" > /dev/null

# Wait a bit
sleep 0.5

# Check trace
echo ""
echo "5. Checking trace output..."
EVENTS=$(sudo cat /sys/kernel/debug/tracing/trace | grep -c "QUANTUM")
echo "Found $EVENTS QUANTUM events"

if [ $EVENTS -gt 0 ]; then
    echo ""
    echo "✅ SUCCESS! eBPF is generating events:"
    sudo cat /sys/kernel/debug/tracing/trace | grep "QUANTUM" | head -5
else
    echo ""
    echo "❌ NO EVENTS FOUND"
    echo "This means bpf_printk is not working or the hook is not executing"
    echo ""
    echo "Let's check the stats map to see if the hook is at least incrementing counters..."
    sudo bpftool map dump name stats 2>/dev/null | head -10
fi
