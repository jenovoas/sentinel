#!/bin/bash
# scripts/test_boot.sh
# Testing Sentinel Init System in QEMU

set -e

PROJECT_ROOT=$(pwd)
INITRD="$PROJECT_ROOT/initramfs.cpio.gz"
KERNEL="/boot/vmlinuz-$(uname -r)"

if [ ! -f "$INITRD" ]; then
    echo "Error: $INITRD not found. Run scripts/build_initramfs.sh first."
    exit 1
fi

if [ ! -f "$KERNEL" ]; then
    # Try common alternatives if the specific version isn't at the root of /boot
    KERNEL=$(ls /boot/vmlinuz-* | head -n 1)
fi

echo "[sentinel-test] Launching Sentinel OS Foundation Core in QEMU..."
echo "[sentinel-test] Kernel: $KERNEL"

qemu-system-x86_64 \
    -kernel "$KERNEL" \
    -initrd "$INITRD" \
    -append "console=ttyS0 quiet panic=1 init=/init" \
    -nographic \
    -m 512M \
    -no-reboot
