#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔧 Sentinel NVIDIA Driver Repair Tool${NC}"
echo "======================================="
KERNEL_VER=$(uname -r)
echo "Target Kernel: $KERNEL_VER"

# 1. Install Headers
echo -e "\n${GREEN}[1/4] Installing Kernel Headers...${NC}"
if ! sudo apt-get install -y linux-headers-$KERNEL_VER; then
    echo -e "${RED}❌ Failed to install headers. Check internet connection.${NC}"
    exit 1
fi

# 2. Rebuild DKMS
echo -e "\n${GREEN}[2/4] Rebuilding NVIDIA Modules (This may take a minute)...${NC}"
if ! sudo dpkg-reconfigure nvidia-kernel-dkms; then
    echo -e "${RED}❌ DKMS build failed.${NC}"
    exit 1
fi

# 3. Load Modules
echo -e "\n${GREEN}[3/4] Loading Kernel Modules...${NC}"
# Unload first just in case partial load
sudo modprobe -r nvidia_drm nvidia_modeset nvidia_uvm nvidia 2>/dev/null || true
if ! sudo modprobe nvidia; then
    echo -e "${RED}❌ Failed to modprobe nvidia.${NC}"
    exit 1
fi

# 4. Verify
echo -e "\n${GREEN}[4/4] Verifying GPU...${NC}"
if nvidia-smi; then
    echo -e "\n${GREEN}✅ SUCCESS: Driver loaded successfully!${NC}"
    echo "Attempting to wake up displays..."
    xrandr --auto
else
    echo -e "\n${RED}❌ ERROR: Driver failed to load even after rebuild.${NC}"
    exit 1
fi
