#!/bin/bash
# TruthSync Audit & Integrity Validator
# Purpose: Validate TruthSync dual-container architecture and performance
# Methodology: Ground Truth (DB/Redis) > Performance (Buffer) > Logic (Server)

set -euo pipefail

# Configuration
readonly AUDIT_DIR="/tmp/truthsync_audit_$(date +%Y%m%d_%H%M%S)"
readonly TRUTHSYNC_DIR="/home/jnovoas/sentinel/truthsync-poc"
readonly FORENSICS_DB="/home/jnovoas/sentinel/forensics/evidence.db"
readonly MATRIX_FILE="$AUDIT_DIR/truthsync_matrix.md"

# Thresholds
readonly MAX_BUFFER_OVERHEAD_US=5.0
readonly BATCH_WINDOW_MS=10

setup_audit() {
    mkdir -p "$AUDIT_DIR"
    {
        echo "# TruthSync Audit Report"
        echo ""
        echo "**Generated**: $(date -Iseconds)"
        echo "**System**: $(uname -a)"
        echo ""
        echo "## Validation Matrix"
        echo ""
        echo "| Componente | Claim | Real | Match | Acción |"
        echo "|------------|-------|------|-------|--------|"
    } > "$MATRIX_FILE"
}

log_section() { echo -e "\n\033[1;34m=== $1 ===\033[0m"; }
log_pass() { echo -e "\033[0;32m✅ $1\033[0m"; }
log_fail() { echo -e "\033[0;31m❌ $1\033[0m"; }
log_info() { echo -e "\033[0;33mℹ️  $1\033[0m"; }

add_to_matrix() { echo "$1" >> "$MATRIX_FILE"; }

check_infrastructure() {
    log_section "A. Infraestructura (Docker/K8s)"
    
    # Check Postgres
    if sudo docker ps --format '{{.Names}}' | grep -q "sentinel-truth-db"; then
        log_pass "Postgres: Running (sentinel-truth-db)"
        add_to_matrix "| Postgres | Running | sentinel-truth-db | ✅ | OK |"
    else
        log_fail "Postgres: NOT FOUND"
        add_to_matrix "| Postgres | Running | Not Found | ❌ | **Start DB** |"
    fi

    # Check Redis
    if sudo docker ps --format '{{.Names}}' | grep -q "sentinel-truth-redis"; then
        log_pass "Redis: Running (sentinel-truth-redis)"
        add_to_matrix "| Redis | Running | sentinel-truth-redis | ✅ | OK |"
    else
        log_fail "Redis: NOT FOUND"
        add_to_matrix "| Redis | Running | Not Found | ❌ | **Start Redis** |"
    fi

    # Check TruthSync Server (Improved Docker Detection)
    local TRUTHSYNC_SERVER=$(sudo docker ps --format "{{.Names}}" | grep -E "truthsync|python" | head -1 || echo "Offline")
    
    if [[ "$TRUTHSYNC_SERVER" != "Offline" ]]; then
        log_pass "TruthSync Server: Running ($TRUTHSYNC_SERVER)"
        add_to_matrix "| API Server | Running | $TRUTHSYNC_SERVER | ✅ | OK |"
    else
        log_info "TruthSync Server: Not running"
        add_to_matrix "| API Server | Running | Offline | ⚠️ | **docker start** |"
    fi
}

check_data_integrity() {
    log_section "B. Integridad de Datos"
    
    # Forensics DB check
    if [[ -f "$FORENSICS_DB" ]]; then
        log_pass "Forensics DB: Found at $FORENSICS_DB"
        add_to_matrix "| Forensics DB | Exists | Yes | ✅ | OK |"
    else
        log_fail "Forensics DB: MISSING ($FORENSICS_DB)"
        add_to_matrix "| Forensics DB | Exists | No | ❌ | **Initialize DB** |"
    fi

    # TruthSync Core Logic Check (Simulation Detection)
    if grep -q "_simulate_processing" "$TRUTHSYNC_DIR/truthsync_server.py"; then
        log_info "TruthSync Logic: Using SIMULATION mode"
        add_to_matrix "| Logic Mode | Real/Sim | Simulation | ⚠️ | Connect Rust |"
    else
        log_pass "TruthSync Logic: Using REAL mode"
        add_to_matrix "| Logic Mode | Real/Sim | Real | ✅ | OK |"
    fi
}

check_performance() {
    log_section "C. Performance Benchmarks"
    
    # Run buffer overhead test
    log_info "Running Shared Memory Buffer Benchmark..."
    local buffer_output=$(python3 "$TRUTHSYNC_DIR/truthsync_buffer.py" 2>/dev/null || echo "FAIL")
    
    if [[ "$buffer_output" == "FAIL" ]]; then
        log_fail "Buffer overhead: Test failed (python dependencies?)"
        add_to_matrix "| Buffer Latency | <${MAX_BUFFER_OVERHEAD_US}μs | N/A | ❌ | Fix python |"
    else
        local overhead=$(echo "$buffer_output" | grep "Buffer overhead:" | awk '{print $3}' | tr -d 'μs')
        if (( $(echo "$overhead < $MAX_BUFFER_OVERHEAD_US" | bc -l) )); then
            log_pass "Buffer overhead: ${overhead}μs (< ${MAX_BUFFER_OVERHEAD_US}μs)"
            add_to_matrix "| Buffer Latency | <${MAX_BUFFER_OVERHEAD_US}μs | ${overhead}μs | ✅ | OK |"
        else
            log_fail "Buffer overhead: ${overhead}μs (Target: < ${MAX_BUFFER_OVERHEAD_US}μs)"
            add_to_matrix "| Buffer Latency | <${MAX_BUFFER_OVERHEAD_US}μs | ${overhead}μs | ❌ | Optimize |"
        fi
    fi

    # Batch window check
    local current_window=$(grep "BATCH_WINDOW_MS =" "$TRUTHSYNC_DIR/truthsync_server.py" | awk '{print $3}')
    if [[ "$current_window" == "$BATCH_WINDOW_MS" ]]; then
        log_pass "Batch Window: ${BATCH_WINDOW_MS}ms (Target match)"
        add_to_matrix "| Batch Window | ${BATCH_WINDOW_MS}ms | ${current_window}ms | ✅ | OK |"
    else
        log_warn "Batch Window: ${current_window}ms (Target: ${BATCH_WINDOW_MS}ms)"
        add_to_matrix "| Batch Window | ${BATCH_WINDOW_MS}ms | ${current_window}ms | ⚠️ | Adjust |"
    fi
}

finalize_audit() {
    log_section "D. Finalización"
    echo "" >> "$MATRIX_FILE"
    echo "---" >> "$MATRIX_FILE"
    echo "**Audit result generated by TruthSync Validator v1.0.0**" >> "$MATRIX_FILE"
    
    echo -e "\n📊 Reporte generado: \033[1m$MATRIX_FILE\033[0m"
    cat "$MATRIX_FILE"
}

# Main
setup_audit
check_infrastructure
check_data_integrity
check_performance
finalize_audit
