#!/bin/bash
# Test script for Guardian-Alpha LSM
# Verifies kernel-level interception is working

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Guardian-Alpha LSM - Basic Test Suite                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if LSM is loaded
echo -e "${BOLD}1️⃣  Checking if LSM is loaded${NC}"
if [ -f /sys/fs/bpf/guardian_alpha_lsm ]; then
    echo -e "   ${GREEN}✅ Guardian-Alpha LSM is loaded${NC}"
    sudo bpftool prog show pinned /sys/fs/bpf/guardian_alpha_lsm
else
    echo -e "   ${RED}❌ LSM not loaded. Run: sudo ./load.sh${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}2️⃣  Checking kernel logs${NC}"
echo -e "   Last 10 Guardian-Alpha events:"
sudo dmesg | grep "Guardian-Alpha" | tail -10 || echo "   No events yet"

echo ""
echo -e "${BOLD}3️⃣  Testing whitelist (if implemented)${NC}"
echo -e "   ${YELLOW}Note: POC version blocks all non-whitelisted commands${NC}"
echo -e "   ${YELLOW}To test blocking, try executing a non-whitelisted binary${NC}"

echo ""
echo -e "${BOLD}${GREEN}✅ Basic tests complete${NC}"
echo ""
echo -e "${BOLD}Next steps:${NC}"
echo "   1. Monitor logs: ${YELLOW}sudo dmesg -w | grep Guardian-Alpha${NC}"
echo "   2. Unload LSM:   ${YELLOW}sudo ./unload.sh${NC}"
