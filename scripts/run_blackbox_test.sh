#!/bin/bash
set -e

# Cleanup
pkill -f "qemu-system-x86_64" || true
pkill -f "mitm_spy.py" || true
pkill -f "cortex_bridge.py" || true
rm -f /tmp/sentinel_cortex.sock /tmp/sentinel_spy.sock

echo "🕵️  STARTING BLACK BOX TEST..."

# 1. Start QEMU (Kernel Server)
echo "🚀 Booting QEMU..."
./scripts/test_boot.sh > qemu_blackbox.log 2>&1 &
sleep 5

# 2. Start MITM Spy
echo "🕵️  Starting MITM Spy..."
python3 -u scripts/mitm_spy.py > spy_output.log 2>&1 &
sleep 2

# 3. Start Bridge (Client to Spy)
echo "🧠 Starting Bridge..."
python3 -u sentinel_core/brain/cortex_bridge.py > bridge_blackbox.log 2>&1 &

# 4. Monitor
echo "👀 Monitoring Spy Output (Ctrl+C to stop)..."
tail -f spy_output.log
