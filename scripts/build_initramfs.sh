#!/bin/bash
# scripts/build_initramfs.sh
# Packaging Sentinel OS Foundation Init into initramfs

set -e

PROJECT_ROOT=$(pwd)
BUILD_DIR="$PROJECT_ROOT/temp_initramfs"
INIT_BIN="$PROJECT_ROOT/sentinel_core/init/target/x86_64-unknown-linux-musl/release/init"
EBPF_OBJ="$PROJECT_ROOT/ebpf/init_kprobe.o"
OUTPUT_FILE="$PROJECT_ROOT/initramfs.cpio.gz"

echo "[sentinel-build] Starting initramfs generation..."

# 1. Clean and create structure
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"/{bin,dev,proc,sys,etc,lib,lib64}

# 2. Copy the Sentinel Init binary as the system's /init
if [ ! -f "$INIT_BIN" ]; then
    echo "Error: $INIT_BIN not found. Run 'cargo build --release' in sentinel_core/init first."
    exit 1
fi
cp "$INIT_BIN" "$BUILD_DIR/init"
chmod +x "$BUILD_DIR/init"

# 3. Copy BusyBox for emergency shell and utilities
BUSYBOX=""
if [ -f "/bin/busybox" ]; then
    BUSYBOX="/bin/busybox"
elif [ -f "/usr/bin/busybox" ]; then
    BUSYBOX="/usr/bin/busybox"
fi

if [ -n "$BUSYBOX" ]; then
    cp "$BUSYBOX" "$BUILD_DIR/bin/busybox"
    # Create symlinks for common tools
    ln -s busybox "$BUILD_DIR/bin/sh"
    ln -s busybox "$BUILD_DIR/bin/ls"
    ln -s busybox "$BUILD_DIR/bin/cat"
    ln -s busybox "$BUILD_DIR/bin/mkdir"
    ln -s busybox "$BUILD_DIR/bin/mount"
else
    echo "Warning: Busybox not found. Debug shell won't be available."
fi

# 4. Copy the Attack PoC (static C binary)
if [ -f "$PROJECT_ROOT/scripts/attack_poc" ]; then
    cp "$PROJECT_ROOT/scripts/attack_poc" "$BUILD_DIR/bin/attack_poc"
    chmod +x "$BUILD_DIR/bin/attack_poc"
fi

# 5. Copy eBPF objects (Init system expects them at relative paths)
# We recreate the path structure expected by the Rust binary: ../../../ebpf/...
mkdir -p "$BUILD_DIR/ebpf"
cp "$EBPF_OBJ" "$BUILD_DIR/ebpf/init_kprobe.o"

# 5. Package into CPIO
cd "$BUILD_DIR"
find . -print0 | cpio --null -ov --format=newc | gzip -9 > "$OUTPUT_FILE"

echo "[sentinel-build] SUCCESS: $OUTPUT_FILE generated."
cd "$PROJECT_ROOT"
# rm -rf "$BUILD_DIR"
