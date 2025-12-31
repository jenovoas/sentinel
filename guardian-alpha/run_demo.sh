#!/bin/bash
set -e

echo "🔮 Sentinel Cortex™ - Phase 6: Quantum-AI Integration Demo"
echo "=========================================================="

# 1. Check Root
if [ "$EUID" -ne 0 ]; then 
  echo "❌ Please run as root (sudo)."
  exit 1
fi

# 2. Cleanup Previous (if any)
echo "🧹 Cleaning up previous instances..."
rm -f /sys/fs/bpf/quantum_ai
# Note: DETACH might be needed if previously attached. bpftool sometimes handles this or we ignore errors.
# We try to detach just in case, suppressing errors
bpftool cgroup detach /sys/fs/cgroup/unified quantum_ai 2>/dev/null || true
# Since it's LSM, it's pinned. We just unpin to unload?
# LSM attachment is permanent until detached or replaced.
# Best effort cleanup:
umount /sys/fs/bpf/quantum_ai 2>/dev/null || true
rm -f /sys/fs/bpf/quantum_ai
# Actually, standard way implies just loading and replacing or removing pin.

# 2.5 Compile eBPF (Ensure latest changes used)
echo "🔨 Compiling eBPF Program..."
clang -g -O2 -target bpf -I/usr/include/x86_64-linux-gnu -c guardian-alpha/quantum_ai_integration.c -o guardian-alpha/quantum_ai_integration.o

# 3. Load BPF Program (and Auto-Attach)
echo "🧠 Loading eBPF Cognitive Kernel..."
# autoattach will create the LSM link. 
# Note: For persistent attachment in production, we'd pin the link, 
# but for this demo, the focus is on the active session.
# We accept that if this shell exits, the link might conceptually disappear 
# if not pinned, but usually pinned programs stay loaded. 
# However, the LINK might disappear. 
# Let's try attempting to pin the link if possible, but standard bpftool load 
# doesn't easily pin links.
# For a demo, 'autoattach' often works if the program stays resident.
bpftool prog load guardian-alpha/quantum_ai_integration.o /sys/fs/bpf/quantum_ai type lsm autoattach

# 4. Attach to LSM Hooks (Handled by autoattach)
echo "🔗 LSM Hooks Attached via Link."

# 5. Initialize Maps (Dummy/Default for demo)
# (Skipped for now, defaults to medium threat in code)

echo "✅ Cognitive Kernel Active."
echo ""
echo "🔊 Starting Quantum-BCI Bridge (Audio Feedback)..."
echo "   (Press Ctrl+C to stop)"

# 6. Run Bridge
# Use the project's virtual environment where dependencies are installed
VENV_PYTHON="/home/jnovoas/sentinel/.venv/bin/python3"

echo "🐍 Using Python: $VENV_PYTHON"
$VENV_PYTHON guardian-alpha/quantum_bci_bridge.py
