#!/bin/bash
# Unload Guardian-Alpha LSM

set -e

BPF_DIR="/sys/fs/bpf/guardian_alpha"

echo "🛑 Unloading Guardian-Alpha LSM..."

# Check if Guardian is loaded
if [ ! -d "$BPF_DIR" ]; then
    echo "✅ Guardian-Alpha is not loaded"
    exit 0
fi

# Remove pinned link first (detach)
if [ -f "$BPF_DIR/guardian_link" ]; then
    echo "🔓 Detaching LSM link..."
    sudo rm -f "$BPF_DIR/guardian_link"
    echo "✅ LSM detached"
fi

# Remove all pinned objects
echo "🧹 Removing pinned objects..."
sudo rm -rf "$BPF_DIR"/*

# Remove directory
if [ -d "$BPF_DIR" ]; then
    sudo rmdir "$BPF_DIR" 2>/dev/null || true
fi

echo ""
echo "✅ Guardian-Alpha LSM unloaded successfully"
echo ""
echo "⚠️  Note: The eBPF program may remain in kernel memory until:"
echo "   1. All references are released"
echo "   2. System reboot (if still attached)"
echo ""

# Verify
if sudo bpftool prog show | grep -q "guardian"; then
    echo "📊 Guardian programs still in kernel:"
    sudo bpftool prog show | grep -A 3 "guardian"
else
    echo "✅ No Guardian programs found in kernel"
fi
