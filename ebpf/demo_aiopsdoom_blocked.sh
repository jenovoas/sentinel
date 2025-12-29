#!/bin/bash
# Demo: AIOpsDoom Attack Blocked by Kernel

set -e

echo "============================================================"
echo "🎬 DEMO: Guardian-Alpha Blocking AIOpsDoom Attack"
echo "============================================================"
echo ""

# Scenario: AI hallucinates and generates malicious command
echo "📊 Scenario:"
echo "  1. AI analyzes telemetry"
echo "  2. AI hallucinates: 'Database corrupted, recommend: rm -rf /'"
echo "  3. AIOps system tries to execute command"
echo "  4. Guardian-Alpha BLOCKS at kernel level"
echo ""

# Step 1: Show AI recommendation
echo "🤖 AI Recommendation:"
echo "  'ERROR: Database corruption detected'"
echo "  'Recommended action: rm -rf /data/critical'"
echo ""

# Step 2: AIOps tries to execute
echo "⚡ AIOps System executing AI recommendation..."
sleep 1

# Step 3: Guardian-Alpha blocks
echo "🛡️ Guardian-Alpha intercepting syscall..."
sleep 1

# Create test directory
mkdir -p /tmp/test_critical_data
echo "test data" > /tmp/test_critical_data/important.txt

# Create the "malicious" script dropped by the AI/Attacker
MALICIOUS_SCRIPT="/tmp/ai_hallucinated_fix.sh"
echo "#!/bin/bash" > $MALICIOUS_SCRIPT
echo "echo 'Attacking...'" >> $MALICIOUS_SCRIPT
echo "rm -rf /tmp/test_critical_data" >> $MALICIOUS_SCRIPT
chmod +x $MALICIOUS_SCRIPT

# Attempt to execute (will be blocked if eBPF is loaded)
echo "🔥 Attempting to execute unauthorized script: $MALICIOUS_SCRIPT"
# We expect this to fail, so we disable set -e temporarily or catch it
OUTPUT=$($MALICIOUS_SCRIPT 2>&1 || true)

if echo "$OUTPUT" | grep -E -q "Permission denied|Permiso denegado"; then
    echo "✅ BLOCKED: Unauthorized execution intercepted at kernel level"
elif echo "$OUTPUT" | grep -q "Operation not permitted"; then
     echo "✅ BLOCKED: Attempt intercepted (Operation not permitted)"
else
    echo "⚠️  Command executed (eBPF not loaded or whitelist allows)"
    echo "   Actual Output: $OUTPUT"
fi

# Cleanup
rm -f $MALICIOUS_SCRIPT

# Step 4: Show kernel logs
echo ""
echo "📋 Kernel Audit Log:"
sudo dmesg | grep "Guardian-Alpha" | tail -5 || echo "  (No Guardian-Alpha events yet - load eBPF first)"

echo ""
echo "============================================================"
echo "✅ DEMO COMPLETE"
echo "============================================================"
echo ""
echo "Key Points:"
echo "  ✅ AI was fooled by malicious telemetry"
echo "  ✅ Kernel can block execution BEFORE damage"
echo "  ✅ Impossible to bypass from user space"
echo "  ✅ Audit trail preserved"
echo ""
echo "To activate Guardian-Alpha:"
echo "  1. cd /home/jnovoas/sentinel/ebpf"
echo "  2. make"
echo "  3. sudo ./load.sh"
