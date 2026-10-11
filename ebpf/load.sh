#!/bin/bash
# Guardian-Alpha LSM Loader

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROG="$SCRIPT_DIR/guardian_cognitive.o"
BPF_DIR="/sys/fs/bpf/guardian_alpha"
PIN="$BPF_DIR/guardian_prog"
LINK_PIN="$BPF_DIR/guardian_link"

echo "🔒 Loading Guardian-Alpha LSM..."

# Ensure attacher exists
if [ ! -f "$SCRIPT_DIR/attacher" ]; then
    echo "⚙️  Compiling attacher tool..."
    clang -g -O2 -Wall -I/usr/include -o "$SCRIPT_DIR/attacher" "$SCRIPT_DIR/attacher.c" -lbpf
fi

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

# Load eBPF program and pin maps (WITHOUT attaching yet)
# We use bpftool here because it works fine for loading and pinning maps
echo "📦 Loading eBPF program and pinning maps..."
sudo bpftool prog load "$PROG" "$PIN" type lsm pinmaps "$BPF_DIR"

# Populate whitelist BEFORE attaching to avoid lockout
echo "📝 Populating whitelist..."
if [ -f "$SCRIPT_DIR/populate_whitelist.sh" ]; then
    bash "$SCRIPT_DIR/populate_whitelist.sh"
else
    echo "⚠️  Warning: populate_whitelist.sh not found! System might freeze if you proceed."
    read -p "Press [Enter] to continue or Ctrl+C to abort..."
fi

# Attach the LSM program using custom attacher
echo "⚓ Attaching Guardian-Alpha LSM..."
sudo "$SCRIPT_DIR/attacher" "$PIN" "$LINK_PIN"

# Verify
if [ -f "$LINK_PIN" ]; then
    echo "✅ Guardian-Alpha LSM loaded and ATTACHED successfully"
    echo ""
    echo "📊 Program Info:"
    sudo bpftool prog show pinned "$PIN"
    echo ""
    echo "🗺️  Pinned Maps:"
    ls -l "$BPF_DIR"
else
    echo "❌ Failed to attach Guardian-Alpha LSM"
    exit 1
fi

# Whitelist populated above.

echo ""
echo "🎉 Guardian-Alpha LSM is now protecting your system!"
echo "⚠️  All non-whitelisted commands will be BLOCKED at kernel level"
