#!/bin/bash
set -e

echo "🔮 Sentinel Cortex™ - Phase 6: Quantum-AI Integration Demo"
echo "=========================================================="

# ============================================================================
# 0. AUTOMATED VALIDATION (Anti-Hallucination Safeguards)
# ============================================================================

# Kernel Version Validation
KERNEL_FULL=$(uname -r)
KERNEL_MAJOR=$(echo "$KERNEL_FULL" | cut -d. -f1)
KERNEL_MINOR=$(echo "$KERNEL_FULL" | cut -d. -f2)

echo "🐧 Kernel version: $KERNEL_FULL"

# Check minimum kernel version (6.1+)
check_kernel_eevdf() {
    local major=$1
    local minor=$2
    
    # EEVDF available in 6.6+ [web:kernelnewbies.org/Linux_6.6]
    if [[ $major -ge 6 ]] && [[ $minor -ge 6 ]]; then
        echo "✅ EEVDF scheduler: Supported (kernel >= 6.6) [web:kernelnewbies.org/Linux_6.6]"
        return 0
    elif [[ $major -ge 6 ]] && [[ $minor -ge 1 ]]; then
        echo "⚠️  EEVDF scheduler: Not available (requires >= 6.6, using CFS)"
        echo "   Current: $KERNEL_FULL | Scheduler: CFS (Completely Fair Scheduler)"
        echo "   Performance may differ from documented benchmarks"
        return 1
    else
        echo "❌ ERROR: Kernel $KERNEL_FULL is below minimum requirement (6.1+)"
        echo "   Please upgrade your kernel to at least 6.1"
        return 2
    fi
}

# Run EEVDF check
check_kernel_eevdf "$KERNEL_MAJOR" "$KERNEL_MINOR"
EEVDF_STATUS=$?

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
clang -g -O2 -target bpf -I/usr/include/x86_64-linux-gnu -c "$(dirname "$0")/quantum_ai_integration.c" -o "$(dirname "$0")/quantum_ai_integration.o"

# 3. Load BPF Program (and Auto-Attach)
echo "🧠 Loading eBPF Cognitive Kernel..."
bpftool prog load "$(dirname "$0")/quantum_ai_integration.o" /sys/fs/bpf/quantum_ai type lsm autoattach

# 4. Attach to LSM Hooks (Handled by autoattach)
echo "🔗 LSM Hooks Attached via Link."

# 6. Run Bridge
# Use the project's virtual environment where dependencies are installed
VENV_PYTHON="/home/jnovoas/sentinel/.venv/bin/python3"
[[ ! -f "$VENV_PYTHON" ]] && VENV_PYTHON="python3"

echo "🐍 Using Python: $VENV_PYTHON"
$VENV_PYTHON "$(dirname "$0")/quantum_bci_bridge.py"
