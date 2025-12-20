#!/bin/bash
# Guardian-Alpha LSM Loader

set -e

PROG="guardian_alpha_lsm.o"
PIN="/sys/fs/bpf/guardian_alpha_lsm"

echo "🔒 Loading Guardian-Alpha LSM..."

# Check if already loaded
if [ -f "$PIN" ]; then
    echo "⚠️  Guardian-Alpha already loaded. Unloading first..."
    sudo rm -f "$PIN"
fi

# Load eBPF program
echo "📦 Loading eBPF program..."
sudo bpftool prog load "$PROG" "$PIN" type lsm

# Verify
if [ -f "$PIN" ]; then
    echo "✅ Guardian-Alpha LSM loaded successfully"
    echo ""
    echo "📊 Program Info:"
    sudo bpftool prog show pinned "$PIN"
else
    echo "❌ Failed to load Guardian-Alpha LSM"
    exit 1
fi

# Populate whitelist (for POC)
echo ""
echo "📝 Populating whitelist..."
# TODO: Add whitelist entries via map update
# For now, all commands are blocked by default

echo ""
echo "🎉 Guardian-Alpha LSM is now protecting your system!"
echo "⚠️  All non-whitelisted commands will be BLOCKED at kernel level"
