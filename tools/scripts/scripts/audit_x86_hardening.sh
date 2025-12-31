#!/bin/bash
# x86 Hardware Audit Script for Debian 13 "Trixie"
# Verifies: Architecture, Intel CET/AMD Shadow Stack, Watchdog, perf_event_paranoid

set -e

echo "========================================="
echo "Sentinel Cortex™ - x86 Hardware Audit"
echo "Debian 13 'Trixie' Hardening Verification"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Architecture Verification
echo "1. Architecture Verification"
echo "----------------------------"
ARCH=$(uname -m)
if [ "$ARCH" == "x86_64" ]; then
    echo -e "${GREEN}✓${NC} Architecture: $ARCH (64-bit)"
else
    echo -e "${RED}✗${NC} Architecture: $ARCH (NOT 64-bit)"
    echo "   WARNING: Debian 13 requires x86_64"
fi

# Check for i386 packages
I386_PKGS=$(dpkg --print-foreign-architectures 2>/dev/null | grep i386 || true)
if [ -z "$I386_PKGS" ]; then
    echo -e "${GREEN}✓${NC} No i386 legacy packages"
else
    echo -e "${YELLOW}⚠${NC} i386 architecture enabled (legacy compatibility)"
fi
echo ""

# 2. Intel CET / AMD Shadow Stack
echo "2. ROP/JOP Mitigations (Intel CET / AMD Shadow Stack)"
echo "------------------------------------------------------"

# Check CPU vendor
CPU_VENDOR=$(lscpu | grep "Vendor ID" | awk '{print $3}')
echo "CPU Vendor: $CPU_VENDOR"

# Intel CET
if grep -q "cet_ibt\|cet_shstk" /proc/cpuinfo 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Intel CET supported (Control-flow Enforcement Technology)"
    grep -o "cet_ibt\|cet_shstk" /proc/cpuinfo | head -2
else
    echo -e "${YELLOW}⚠${NC} Intel CET not detected"
fi

# AMD Shadow Stack
if grep -q "shadow_stack" /proc/cpuinfo 2>/dev/null; then
    echo -e "${GREEN}✓${NC} AMD Shadow Stack supported"
else
    echo -e "${YELLOW}⚠${NC} AMD Shadow Stack not detected"
fi

# Kernel support
if grep -q "CONFIG_X86_KERNEL_IBT=y" /boot/config-$(uname -r) 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Kernel has IBT support (CONFIG_X86_KERNEL_IBT=y)"
else
    echo -e "${YELLOW}⚠${NC} Kernel IBT support not found"
fi
echo ""

# 3. Hardware Watchdog
echo "3. Hardware Watchdog (Kill Switch)"
echo "----------------------------------"

# Check for watchdog modules
WATCHDOG_MODULES=$(lsmod | grep -E "iTCO_wdt|sp5100_tco" || true)
if [ -n "$WATCHDOG_MODULES" ]; then
    echo -e "${GREEN}✓${NC} Watchdog module loaded:"
    echo "$WATCHDOG_MODULES"
else
    echo -e "${RED}✗${NC} No watchdog module loaded"
    echo "   Expected: iTCO_wdt (Intel) or sp5100_tco (AMD)"
fi

# Check for watchdog device
if [ -e "/dev/watchdog0" ]; then
    echo -e "${GREEN}✓${NC} Watchdog device: /dev/watchdog0"
    ls -l /dev/watchdog*
    
    # Check timeout
    if [ -r "/sys/class/watchdog/watchdog0/timeout" ]; then
        TIMEOUT=$(cat /sys/class/watchdog/watchdog0/timeout)
        echo "   Timeout: ${TIMEOUT}s"
    fi
else
    echo -e "${RED}✗${NC} Watchdog device not found (/dev/watchdog0)"
fi
echo ""

# 4. perf_event_paranoid
echo "4. Observability vs Security (perf_event_paranoid)"
echo "---------------------------------------------------"

PERF_PARANOID=$(sysctl -n kernel.perf_event_paranoid 2>/dev/null || echo "not set")
echo "Current value: $PERF_PARANOID"

case $PERF_PARANOID in
    -1)
        echo -e "${YELLOW}⚠${NC} Level: -1 (MINIMAL security, MAXIMUM observability)"
        echo "   Recommendation: Only for development"
        ;;
    0)
        echo -e "${YELLOW}⚠${NC} Level: 0 (MEDIUM security, DEEP observability)"
        echo "   Recommendation: Isolated systems only"
        ;;
    1)
        echo -e "${GREEN}✓${NC} Level: 1 (BALANCED)"
        echo "   Recommendation: Good for most production"
        ;;
    2)
        echo -e "${GREEN}✓${NC} Level: 2 (HIGH security, USER-SPACE observability)"
        echo "   Recommendation: Production exposed systems"
        ;;
    3|4)
        echo -e "${GREEN}✓${NC} Level: $PERF_PARANOID (MAXIMUM security)"
        echo "   Recommendation: High-security environments"
        ;;
    "not set")
        echo -e "${YELLOW}⚠${NC} Not configured (using kernel default)"
        ;;
    *)
        echo -e "${YELLOW}⚠${NC} Unknown value: $PERF_PARANOID"
        ;;
esac
echo ""

# 5. Summary and Recommendations
echo "========================================="
echo "Summary and Recommendations"
echo "========================================="
echo ""

# Calculate score
SCORE=0
MAX_SCORE=5

[ "$ARCH" == "x86_64" ] && ((SCORE++))
grep -q "cet_ibt\|cet_shstk\|shadow_stack" /proc/cpuinfo 2>/dev/null && ((SCORE++))
[ -n "$WATCHDOG_MODULES" ] && ((SCORE++))
[ -e "/dev/watchdog0" ] && ((SCORE++))
[ "$PERF_PARANOID" != "not set" ] && ((SCORE++))

echo "Hardening Score: $SCORE/$MAX_SCORE"
echo ""

if [ $SCORE -eq $MAX_SCORE ]; then
    echo -e "${GREEN}✓ EXCELLENT${NC} - All hardening features enabled"
elif [ $SCORE -ge 3 ]; then
    echo -e "${YELLOW}⚠ GOOD${NC} - Most hardening features enabled"
    echo "   Review warnings above for improvements"
else
    echo -e "${RED}✗ NEEDS IMPROVEMENT${NC} - Critical hardening missing"
    echo "   Address errors above immediately"
fi
echo ""

# Recommendations
echo "Recommendations:"
echo "----------------"

if [ "$ARCH" != "x86_64" ]; then
    echo -e "${RED}CRITICAL:${NC} Migrate to x86_64 architecture"
fi

if ! grep -q "cet_ibt\|cet_shstk\|shadow_stack" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}WARNING:${NC} Consider upgrading CPU for ROP/JOP protection"
fi

if [ -z "$WATCHDOG_MODULES" ]; then
    echo -e "${YELLOW}WARNING:${NC} Load watchdog module:"
    if [ "$CPU_VENDOR" == "GenuineIntel" ]; then
        echo "   sudo modprobe iTCO_wdt"
        echo "   echo 'iTCO_wdt' | sudo tee -a /etc/modules"
    else
        echo "   sudo modprobe sp5100_tco"
        echo "   echo 'sp5100_tco' | sudo tee -a /etc/modules"
    fi
fi

if [ "$PERF_PARANOID" == "not set" ] || [ "$PERF_PARANOID" -lt 1 ]; then
    echo -e "${YELLOW}INFO:${NC} Consider setting perf_event_paranoid:"
    echo "   Production: sudo sysctl -w kernel.perf_event_paranoid=2"
    echo "   Isolated:   sudo sysctl -w kernel.perf_event_paranoid=0"
fi

echo ""
echo "========================================="
echo "Audit Complete"
echo "========================================="
