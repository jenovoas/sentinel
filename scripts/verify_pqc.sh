#!/bin/bash
set -u

echo "🔐 [PHASE 10] Verifying Post-Quantum Secure Channel..."

# 1. Cleanup
pkill -f "qemu-system-x86_64" || true
pkill -f "cortex_bridge.py" || true
rm -f /tmp/sentinel_cortex.sock

# 2. Start Cortex Bridge (The 'Brain' Server)
echo "🧠 Starting Cortex Bridge (Python)..."
# Use unbuffered output to catch logs immediately
python3 -u sentinel_core/brain/cortex_bridge.py > bridge.log 2>&1 &
BRIDGE_PID=$!

# Give it a moment to create the socket
sleep 2

# 3. Start Sentinel Init (QEMU)
echo "🚀 Booting Sentinel Init..."
./scripts/test_boot.sh > qemu.log 2>&1 &
QEMU_PID=$!

# 4. Monitor for Success
echo "👀 Monitoring Handshake & Encrypted Traffic..."
MAX_WAIT=30
START_TIME=$(date +%s)

SUCCESS_HANDSHAKE=0
SUCCESS_REPORT=0

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED -gt $MAX_WAIT ]; then
        echo "❌ Timeout waiting for Secure Channel."
        break
    fi

    # Check Bridge Log
    if grep -q "Shared Secret Established" bridge.log; then
        if [ $SUCCESS_HANDSHAKE -eq 0 ]; then
            echo "✅ Handshake Complete! (X25519+ChaCha20)"
            SUCCESS_HANDSHAKE=1
        fi
    fi

    if grep -q "SECURE-REPORT" bridge.log; then
        echo "✅ Encrypted Threat Report Received & Decrypted!"
        SUCCESS_REPORT=1
        break
    fi

    sleep 1
done

# 5. Cleanup
kill $BRIDGE_PID
kill $QEMU_PID
pkill -f "qemu-system-x86_64"

if [ $SUCCESS_HANDSHAKE -eq 1 ] && [ $SUCCESS_REPORT -eq 1 ]; then
    echo "🏆 PHASE 10 VERIFICATION SUCCESSFUL."
    exit 0
else
    echo "⚠️ Verification Failed. Check bridge.log and qemu.log."
    exit 1
fi
