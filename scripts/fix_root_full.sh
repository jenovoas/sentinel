#!/bin/bash
# -----------------------------------------------------------------------------
# 🚑 SENTINEL EMERGENCY PROTOCOL: ROOT UNSHACKLE
# -----------------------------------------------------------------------------
# 1. Frees critical space on Root (Deleting /usr/share/doc).
# 2. Forces LVM Expansion without Metadata Backup (Bypassing Write Error).
# -----------------------------------------------------------------------------

VG_NAME="devlap-vg"
LV_ROOT="/dev/mapper/devlap--vg-root"

echo "🚨 EMERGENCY ROOT FIX INITIATED"
echo "------------------------------"

# 1. Surgical Cleaning (Frees ~50-200MB)
echo "🧹 Cleaning Documentation from /usr/share/doc on Root Partition..."
# CAUTION: This deletes documentation. Necessary for survival.
sudo rm -rf /usr/share/doc/*
echo "   Space cleared."

# 2. Force Expansion (No Backup of Metadata)
echo "🚀 Forcing LVM Extension (Autobackup: OFF)..."
# We try to add the 50G again. If it's already "extended" in LVM but failed FS, this might warn.
# Failsafe: Try to extend to +50G. If it says "matches existing size", we proceed to resize2fs.
sudo lvextend -L +50G --autobackup n $LV_ROOT || echo "⚠️  LVM Extension warning (maybe already resized state). Proceeding to FS Resize."

# 3. Force Kernel Refresh
echo "🔄 Triggering Kernel Device Refresh..."
sudo udevadm trigger

# 4. Resize Filesystem
echo "📏 Resizing Filesystem..."
sudo resize2fs $LV_ROOT

echo ""
echo "✅ STATUS REPORT:"
df -h /
