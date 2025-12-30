#!/bin/bash
set -u

# Cleanup
pkill -f guardian_beta.py > /dev/null 2>&1
pkill -f qemu-system-x86_64 > /dev/null 2>&1

echo "🛡️ Starting Guardian Beta..."
python3 -u /home/jnovoas/sentinel/sentinel_core/brain/guardian_beta.py > /tmp/guardian_crash_final.log 2>&1 &
BETA_PID=$!
sleep 2

echo "🖥️ Starting Sentinel QEMU..."
./scripts/test_boot.sh > /dev/null 2>&1 &
QEMU_PID=$!

echo "⏳ Allowing system to stabilize (15s)..."
sleep 15

echo "❄️ FREEZING QEMU (Simulating Panic/Compromise)..."
kill -STOP $QEMU_PID

echo "👀 Watching for Guardian Reaction (Wait 5s)..."
sleep 5

echo "📋 LOG CONTENTS:"
cat /tmp/guardian_crash_final.log

# Cleanup
echo "🧹 Cleaning up..."
kill -9 $BETA_PID > /dev/null 2>&1
kill -9 $QEMU_PID > /dev/null 2>&1
