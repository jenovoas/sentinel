#!/bin/bash
# Sentinel Cortex Pre-flight Check
# Validates system readiness before deployment
# Usage: sudo ./sentinel_preflight.sh [--json]


# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Output mode
JSON_MODE=false
if [[ "$1" == "--json" ]]; then
    JSON_MODE=true
fi

# Results storage
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0
RESULTS=()

log_check() {
    local status=$1
    local name=$2
    local message=$3
    
    if $JSON_MODE; then
        RESULTS+=("{\"check\":\"$name\",\"status\":\"$status\",\"message\":\"$message\"}")
    else
        case $status in
            "PASS")
                echo -e "${GREEN}✅ $name${NC}: $message"
                ;;
            "FAIL")
                echo -e "${RED}❌ $name${NC}: $message"
                ;;
            "WARN")
                echo -e "${YELLOW}⚠️  $name${NC}: $message"
                ;;
        esac
    fi
    
    case $status in
        "PASS") ((CHECKS_PASSED++)) ;;
        "FAIL") ((CHECKS_FAILED++)) ;;
        "WARN") ((CHECKS_WARNING++)) ;;
    esac
}

# Header
if ! $JSON_MODE; then
    echo "🛡️  Sentinel Cortex Pre-flight Check"
    echo "===================================="
    echo ""
fi

# 1. Root Check
if [[ $EUID -ne 0 ]]; then
    log_check "FAIL" "Root Privileges" "Must run as root (sudo)"
    exit 1
else
    log_check "PASS" "Root Privileges" "Running as root"
fi

# 2. Kernel Version
KERNEL_VERSION=$(uname -r)
KERNEL_MAJOR=$(echo "$KERNEL_VERSION" | cut -d. -f1)
KERNEL_MINOR=$(echo "$KERNEL_VERSION" | cut -d. -f2)

if [[ $KERNEL_MAJOR -ge 6 ]] && [[ $KERNEL_MINOR -ge 1 ]]; then
    log_check "PASS" "Kernel Version" "$KERNEL_VERSION (>= 6.1 required)"
else
    log_check "FAIL" "Kernel Version" "$KERNEL_VERSION (6.1+ required for eBPF LSM)"
fi

# 3. eBPF Support
if command -v bpftool &> /dev/null; then
    log_check "PASS" "bpftool" "Installed"
    
    # Check eBPF features
    if bpftool feature probe kernel 2>/dev/null | grep -q "have_bpf_lsm_prog_type"; then
        log_check "PASS" "eBPF LSM Support" "Kernel supports LSM programs"
    else
        log_check "WARN" "eBPF LSM Support" "LSM support unclear, may need CONFIG_BPF_LSM=y"
    fi
else
    log_check "FAIL" "bpftool" "Not installed (required for eBPF management)"
fi

# 4. Clang/LLVM
if command -v clang &> /dev/null; then
    CLANG_VERSION=$(clang --version | head -n1)
    log_check "PASS" "Clang Compiler" "$CLANG_VERSION"
else
    log_check "FAIL" "Clang Compiler" "Not installed (required for eBPF compilation)"
fi

# 5. Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_check "PASS" "Python 3" "$PYTHON_VERSION"
else
    log_check "FAIL" "Python 3" "Not installed"
fi

# 6. Rust/Cargo
if command -v cargo &> /dev/null; then
    RUST_VERSION=$(cargo --version)
    log_check "PASS" "Rust/Cargo" "$RUST_VERSION"
else
    log_check "WARN" "Rust/Cargo" "Not installed (needed to rebuild sctl/sip)"
fi

# 7. Ollama (AI)
if command -v ollama &> /dev/null; then
    if pgrep -x ollama > /dev/null; then
        log_check "PASS" "Ollama Service" "Running"
        
        # Check for llama3.2 model
        if ollama list 2>/dev/null | grep -q "llama3.2"; then
            log_check "PASS" "Llama 3.2 Model" "Installed"
        else
            log_check "WARN" "Llama 3.2 Model" "Not found (run: ollama pull llama3.2:3b)"
        fi
    else
        log_check "WARN" "Ollama Service" "Installed but not running"
    fi
else
    log_check "WARN" "Ollama" "Not installed (required for SemSH)"
fi

# 8. PostgreSQL
if command -v psql &> /dev/null || docker ps 2>/dev/null | grep -q postgres; then
    if docker ps 2>/dev/null | grep -q postgres; then
        log_check "PASS" "PostgreSQL" "Running (Docker)"
    elif pgrep -x postgres > /dev/null; then
        log_check "PASS" "PostgreSQL" "Running (Native)"
    else
        log_check "WARN" "PostgreSQL" "Installed but not running"
    fi
else
    log_check "WARN" "PostgreSQL" "Not detected (optional for SemSH history)"
fi

# 9. Sentinel Components
SENTINEL_ROOT="/home/jnovoas/sentinel"
if [[ -d "$SENTINEL_ROOT" ]]; then
    log_check "PASS" "Sentinel Repository" "Found at $SENTINEL_ROOT"
    
    # Check key binaries
    if [[ -f "$SENTINEL_ROOT/guardian-alpha/sentinel_relay" ]]; then
        log_check "PASS" "Sentinel Relay Binary" "Compiled"
    else
        log_check "WARN" "Sentinel Relay Binary" "Not found (run: make in guardian-alpha/)"
    fi
    
    if command -v sctl &> /dev/null; then
        log_check "PASS" "sctl Command" "Installed globally"
    else
        log_check "WARN" "sctl Command" "Not in PATH (run: sudo ln -sf tools/sctl_bin /usr/local/bin/sctl)"
    fi
    
    if command -v sip &> /dev/null; then
        log_check "PASS" "sip Command" "Installed globally"
    else
        log_check "WARN" "sip Command" "Not in PATH"
    fi
else
    log_check "FAIL" "Sentinel Repository" "Not found at $SENTINEL_ROOT"
fi

# 10. Shared Memory
SHM_DIR="/var/run/sentinel"
if [[ -d "$SHM_DIR" ]]; then
    log_check "PASS" "SHM Directory" "$SHM_DIR exists"
    
    if [[ -f "$SHM_DIR/truthsync_shm" ]]; then
        SHM_SIZE=$(stat -c%s "$SHM_DIR/truthsync_shm")
        log_check "PASS" "TruthSync SHM" "Mounted (${SHM_SIZE} bytes)"
    else
        log_check "WARN" "TruthSync SHM" "Not created (will be created on first start)"
    fi
else
    log_check "WARN" "SHM Directory" "Not created (will be created on first start)"
fi

# 11. CPU Features
if grep -q "aes" /proc/cpuinfo; then
    log_check "PASS" "AES-NI Support" "CPU supports hardware AES"
else
    log_check "WARN" "AES-NI Support" "Not detected (crypto will be slower)"
fi

if grep -q "avx2" /proc/cpuinfo; then
    log_check "PASS" "AVX2 Support" "CPU supports SIMD instructions"
else
    log_check "WARN" "AVX2 Support" "Not detected"
fi

# 12. Memory
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [[ $TOTAL_MEM -ge 4 ]]; then
    log_check "PASS" "System Memory" "${TOTAL_MEM}GB (>= 4GB recommended)"
else
    log_check "WARN" "System Memory" "${TOTAL_MEM}GB (4GB+ recommended)"
fi

# Summary
if $JSON_MODE; then
    echo "{"
    echo "  \"checks_passed\": $CHECKS_PASSED,"
    echo "  \"checks_failed\": $CHECKS_FAILED,"
    echo "  \"checks_warning\": $CHECKS_WARNING,"
    echo "  \"results\": ["
    for i in "${!RESULTS[@]}"; do
        echo "    ${RESULTS[$i]}"
        if [[ $i -lt $((${#RESULTS[@]} - 1)) ]]; then
            echo ","
        fi
    done
    echo "  ]"
    echo "}"
else
    echo ""
    echo "===================================="
    echo "Summary:"
    echo -e "  ${GREEN}Passed${NC}  : $CHECKS_PASSED"
    echo -e "  ${RED}Failed${NC}  : $CHECKS_FAILED"
    echo -e "  ${YELLOW}Warnings${NC}: $CHECKS_WARNING"
    echo ""
    
    if [[ $CHECKS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}✅ System is ready for Sentinel Cortex deployment${NC}"
        exit 0
    else
        echo -e "${RED}❌ Critical issues detected. Fix failures before deployment.${NC}"
        exit 1
    fi
fi
