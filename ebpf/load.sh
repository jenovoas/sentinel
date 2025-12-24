#!/bin/bash
# Guardian-Alpha LSM Loader

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROG="$SCRIPT_DIR/guardian_alpha_lsm.o"
BPF_DIR="/sys/fs/bpf/guardian_alpha"
PIN="$BPF_DIR/guardian_prog"

echo "🔒 Loading Guardian-Alpha LSM..."

# Ensure BPF filesystem directory exists
if [ ! -d "$BPF_DIR" ]; then
    echo "📁 Creating BPF directory $BPF_DIR..."
    sudo mkdir -p "$BPF_DIR"
fi

# Check if already loaded and clean up
if [ -f "$PIN" ]; then
    echo "⚠️  Guardian-Alpha already loaded. Unloading first..."
    sudo rm -rf "$BPF_DIR"/*
fi

# Load eBPF program and pin maps
echo "📦 Loading eBPF program and pinning maps..."
sudo bpftool prog load "$PROG" "$PIN" type lsm pinmaps "$BPF_DIR"

# Explicitly ATTACH the program to the LSM hook
echo "⚓ Attaching to LSM hook: bprm_check_security..."
sudo bpftool prog attach pinned "$PIN" lsm bprm_check_security

# Verify
if [ -f "$PIN" ]; then
    echo "✅ Guardian-Alpha LSM loaded and ATTACHED successfully"
    echo ""
    echo "📊 Program Info:"
    sudo bpftool prog show pinned "$PIN"
    echo ""
    echo "🗺️  Pinned Maps:"
    ls -l "$BPF_DIR"
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
