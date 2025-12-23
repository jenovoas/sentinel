#!/bin/bash
# Unload Guardian-Alpha LSM

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BOLD}Unloading Guardian-Alpha LSM...${NC}"

# Find Guardian programs
PROG_IDS=$(sudo bpftool prog show | grep -A 1 "guardian" | grep -oP '^\d+' || true)

if [ -n "$PROG_IDS" ]; then
    echo "Found Guardian programs: $PROG_IDS"
    
    # Try to unload each program
    for ID in $PROG_IDS; do
        echo "Attempting to unload program ID $ID..."
        
        # LSM programs cannot be unloaded while attached
        # We can only remove the pinned reference
        if [ -f /sys/fs/bpf/guardian_alpha_lsm ]; then
            sudo rm -f /sys/fs/bpf/guardian_alpha_lsm
            echo -e "${GREEN}✅ Removed pinned reference${NC}"
        fi
    done
    
    echo ""
    echo -e "${YELLOW}⚠️  Note: LSM programs remain in kernel until reboot${NC}"
    echo -e "${YELLOW}   This is normal eBPF LSM behavior for security${NC}"
else
    echo -e "${GREEN}✅ No Guardian programs found${NC}"
fi

# Final verification
echo ""
if sudo bpftool prog show | grep -q guardian; then
    echo -e "${YELLOW}📊 Guardian programs still in kernel (expected):${NC}"
    sudo bpftool prog show | grep -A 3 guardian
    echo ""
    echo -e "${YELLOW}💡 To fully remove: reboot the system${NC}"
else
    echo -e "${GREEN}✅ Verified: No Guardian programs loaded${NC}"
fi
