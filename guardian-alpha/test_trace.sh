#!/bin/bash
echo "Clearing trace buffer..."
sudo sh -c "echo > /sys/kernel/debug/tracing/trace"

echo "Executing test command..."
/bin/ls > /dev/null

echo "Waiting for events..."
sleep 1

echo "Checking trace output:"
sudo cat /sys/kernel/debug/tracing/trace | grep -i quantum | head -20
