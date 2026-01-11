#!/bin/bash
# -----------------------------------------------------------------------------
# 🛡️ SENTINEL INFRASTRUCTURE: ROOT EXPANSION
# -----------------------------------------------------------------------------
# Expands the Root Logical Volume to use available Volume Group space.
# -----------------------------------------------------------------------------

VG_NAME="devlap-vg"
LV_ROOT="/dev/mapper/devlap--vg-root"

# Detect VG Name dynamically if needed (parse vgs output? sudo required)
# We assume 'devlap-vg' based on lsblk output 'devlap--vg-root' (LVM double dash escaping)

echo "🔍 Checking Volume Group space..."

# Get Free Space in VG
FREE_SPACE=$(sudo vgs --noheadings -o vg_free --units g --nosuffix $VG_NAME | sed 's/^[[:space:]]*//' | cut -d',' -f1)

echo "   Free Space detected: ${FREE_SPACE}G"

# Check if we have room (e.g. > 10G)
if (( $(echo "$FREE_SPACE > 10" | bc -l) )); then
    echo "✅ Sufficient space found. Expanding Root..."
    
    # 1. Extend LV (+20GB safe increment, or all?)
    # Let's add 50GB to be safe for AI models.
    # Check if free space > 50.
    
    TARGET_ADD="20G"
    if (( $(echo "$FREE_SPACE > 50" | bc -l) )); then
        TARGET_ADD="50G"
    fi
    
    echo "🚀 Extending Root by +$TARGET_ADD..."
    sudo lvextend -L +$TARGET_ADD $LV_ROOT
    
    echo "🔄 Resizing Filesystem..."
    sudo resize2fs $LV_ROOT
    
    echo "✅ ROOT EXPANSION COMPLETE."
    df -h /
else
    echo "⚠️  Not enough free space in VG ($FREE_SPACE GB). Cannot expand."
    exit 1
fi
