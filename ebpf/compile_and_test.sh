#!/bin/bash
# Guardian-Alpha eBPF LSM Compilation Script
# Compiles both LSM implementations with full validation

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Guardian-Alpha eBPF LSM Compilation                     ║"
echo "║  Kernel-Level AI Safety Enforcement                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Pre-flight checks
echo -e "${BOLD}🔍 Pre-flight Checks${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Kernel version
KERNEL_VERSION=$(uname -r)
echo -e "Kernel Version: ${GREEN}${KERNEL_VERSION}${NC}"

# 2. BPF_LSM support
if zcat /proc/config.gz 2>/dev/null | grep -q "CONFIG_BPF_LSM=y"; then
    echo -e "BPF_LSM Support: ${GREEN}✅ Enabled${NC}"
else
    echo -e "BPF_LSM Support: ${RED}❌ Not found${NC}"
    echo "Note: Continuing anyway, may be enabled but not visible"
fi

# 3. BTF support
if [ -f /sys/kernel/btf/vmlinux ]; then
    BTF_SIZE=$(stat -c%s /sys/kernel/btf/vmlinux)
    echo -e "BTF Support: ${GREEN}✅ Available${NC} (${BTF_SIZE} bytes)"
else
    echo -e "BTF Support: ${RED}❌ Not available${NC}"
    exit 1
fi

# 4. Tools
echo -n "clang: "
if command -v clang &> /dev/null; then
    CLANG_VERSION=$(clang --version | head -1)
    echo -e "${GREEN}✅${NC} ${CLANG_VERSION}"
else
    echo -e "${RED}❌ Not found${NC}"
    exit 1
fi

echo -n "llvm-strip: "
if command -v llvm-strip &> /dev/null; then
    echo -e "${GREEN}✅ Found${NC}"
else
    echo -e "${RED}❌ Not found${NC}"
    exit 1
fi

echo -n "bpftool: "
if command -v bpftool &> /dev/null; then
    BPFTOOL_VERSION=$(bpftool version | head -1)
    echo -e "${GREEN}✅${NC} ${BPFTOOL_VERSION}"
else
    echo -e "${RED}❌ Not found${NC}"
    exit 1
fi

echo ""
echo -e "${BOLD}🔨 Compilation${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -f guardian_alpha_lsm.o lsm_ai_guardian.o

# Compile Guardian Alpha LSM (Basic)
echo ""
echo -e "${BOLD}1️⃣  Compiling guardian_alpha_lsm.c (Basic Version)${NC}"
echo "   → Whitelist-based execve interceptor"

clang -g -O2 -target bpf -D__TARGET_ARCH_x86 \
    -I/usr/include/x86_64-linux-gnu \
    -c guardian_alpha_lsm.c -o guardian_alpha_lsm.o

if [ $? -eq 0 ]; then
    llvm-strip -g guardian_alpha_lsm.o
    SIZE=$(stat -c%s guardian_alpha_lsm.o)
    echo -e "   ${GREEN}✅ Success${NC} (${SIZE} bytes)"
else
    echo -e "   ${RED}❌ Failed${NC}"
    exit 1
fi

# Compile AI Guardian LSM (Advanced)
echo ""
echo -e "${BOLD}2️⃣  Compiling lsm_ai_guardian.c (Advanced Version)${NC}"
echo "   → AI agent tracking + dynamic whitelist"

clang -g -O2 -target bpf -D__TARGET_ARCH_x86 \
    -I/usr/include/x86_64-linux-gnu \
    -c lsm_ai_guardian.c -o lsm_ai_guardian.o

if [ $? -eq 0 ]; then
    llvm-strip -g lsm_ai_guardian.o
    SIZE=$(stat -c%s lsm_ai_guardian.o)
    echo -e "   ${GREEN}✅ Success${NC} (${SIZE} bytes)"
else
    echo -e "   ${RED}❌ Failed${NC}"
    exit 1
fi

# Verification
echo ""
echo -e "${BOLD}🔍 Verification${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo -e "${BOLD}guardian_alpha_lsm.o:${NC}"
file guardian_alpha_lsm.o
echo ""
llvm-objdump -h guardian_alpha_lsm.o | grep -E "lsm|maps|license"

echo ""
echo -e "${BOLD}lsm_ai_guardian.o:${NC}"
file lsm_ai_guardian.o
echo ""
llvm-objdump -h lsm_ai_guardian.o | grep -E "lsm|maps|license"

# Summary
echo ""
echo -e "${BOLD}${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  ✅ COMPILATION SUCCESSFUL                                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BOLD}📦 Compiled Modules:${NC}"
ls -lh *.o | grep -E "guardian_alpha_lsm|lsm_ai_guardian"

echo ""
echo -e "${BOLD}🚀 Next Steps:${NC}"
echo "   1. Load basic version:    ${YELLOW}sudo ./load.sh${NC}"
echo "   2. Load advanced version: ${YELLOW}sudo ./load_ai_guardian.sh${NC}"
echo "   3. Run tests:             ${YELLOW}sudo ./test_lsm_basic.sh${NC}"
echo ""
echo -e "${GREEN}Ready to protect your kernel! 🛡️${NC}"
