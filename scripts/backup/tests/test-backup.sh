#!/bin/bash
#
# Sentinel Backup System - Automated Tests
#
# This script runs comprehensive tests on the backup system to ensure
# all components are working correctly.
#
# Usage:
#   ./test-backup.sh
#
# Exit Codes:
#   0 - All tests passed
#   1 - One or more tests failed
#

set -euo pipefail

# ============================================================================
# SETUP
# ============================================================================

# Get script directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BACKUP_SCRIPT_DIR="$SCRIPT_DIR/.."

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# ============================================================================
# TEST FRAMEWORK
# ============================================================================

#
# Run a test
#
# Args:
#   $1 - Test name
#   $2 - Test command
#
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_RUN++))
    
    echo -n "Test $TESTS_RUN: $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✓ PASSED"
        ((TESTS_PASSED++))
        return 0
    else
        echo "✗ FAILED"
        ((TESTS_FAILED++))
        return 1
    fi
}

# ============================================================================
# TESTS
# ============================================================================

#
# Test 1: Check if backup script exists
#
test_backup_script_exists() {
    [[ -f "$BACKUP_SCRIPT_DIR/backup.sh" ]]
}

#
# Test 2: Check if backup script is executable
#
test_backup_script_executable() {
    [[ -x "$BACKUP_SCRIPT_DIR/backup.sh" ]]
}

#
# Test 3: Check if all modules exist
#
test_modules_exist() {
    [[ -f "$BACKUP_SCRIPT_DIR/lib/config.sh" ]] && \
    [[ -f "$BACKUP_SCRIPT_DIR/lib/logging.sh" ]] && \
    [[ -f "$BACKUP_SCRIPT_DIR/lib/notifications.sh" ]] && \
    [[ -f "$BACKUP_SCRIPT_DIR/lib/validation.sh" ]]
}

#
# Test 4: Check if PostgreSQL container is running
#
test_postgres_running() {
    docker ps | grep -q "sentinel-postgres"
}

#
# Test 5: Check if can connect to PostgreSQL
#
test_postgres_connection() {
    docker exec sentinel-postgres psql -U sentinel_user -d sentinel_db -c "SELECT 1;" > /dev/null 2>&1
}

#
# Test 6: Check if backup directory exists or can be created
#
test_backup_directory() {
    local backup_dir="/var/backups/sentinel/postgres"
    [[ -d "$backup_dir" ]] || mkdir -p "$backup_dir" 2>/dev/null
}

#
# Test 7: Check if backup directory is writable
#
test_backup_directory_writable() {
    local backup_dir="/var/backups/sentinel/postgres"
    [[ -w "$backup_dir" ]] || [[ -w "$(dirname "$backup_dir")" ]]
}

#
# Test 8: Test configuration loading
#
test_config_loading() {
    # Just check if .env exists or can load from environment
    local project_root="$(cd "$BACKUP_SCRIPT_DIR/../.." && pwd)"
    [[ -f "$project_root/.env" ]] || [[ -n "${POSTGRES_CONTAINER:-}" ]]
}

#
# Test 9: Test backup script runs without errors
#
test_backup_script_syntax() {
    bash -n "$BACKUP_SCRIPT_DIR/backup.sh"
}

#
# Test 10: Create test backup
#
test_create_backup() {
    # Set test environment
    local test_backup_dir="/tmp/sentinel-backup-test-$$"
    
    # Create test directory
    mkdir -p "$test_backup_dir"
    
    # Run backup with test configuration
    BACKUP_DIR="$test_backup_dir" \
    POSTGRES_CONTAINER="sentinel-postgres" \
    POSTGRES_USER="sentinel_user" \
    POSTGRES_DB="sentinel_db" \
    LOG_TO_STDOUT=false \
    WEBHOOK_ENABLED=false \
    S3_ENABLED=false \
    MINIO_ENABLED=false \
    ENCRYPT_ENABLED=false \
    "$BACKUP_SCRIPT_DIR/backup.sh" > /dev/null 2>&1
    
    local result=$?
    
    # Check if backup was created
    local backup_count=$(ls -1 "$test_backup_dir"/sentinel_backup_*.sql.gz 2>/dev/null | wc -l)
    
    # Cleanup
    rm -rf "$test_backup_dir"
    
    [[ $result -eq 0 ]] && [[ $backup_count -gt 0 ]]
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo "========================================="
    echo "Sentinel Backup System - Automated Tests"
    echo "========================================="
    echo ""
    
    # Run tests
    run_test "Backup script exists" "test_backup_script_exists"
    run_test "Backup script is executable" "test_backup_script_executable"
    run_test "All modules exist" "test_modules_exist"
    run_test "PostgreSQL container running" "test_postgres_running"
    run_test "PostgreSQL connection" "test_postgres_connection"
    run_test "Backup directory accessible" "test_backup_directory"
    run_test "Backup directory writable" "test_backup_directory_writable"
    run_test "Configuration loading" "test_config_loading"
    run_test "Backup script syntax" "test_backup_script_syntax"
    run_test "Create backup" "test_create_backup"
    
    # Summary
    echo ""
    echo "========================================="
    echo "Test Summary"
    echo "========================================="
    echo "Total tests: $TESTS_RUN"
    echo "Passed: $TESTS_PASSED"
    echo "Failed: $TESTS_FAILED"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo "✓ All tests passed!"
        exit 0
    else
        echo "✗ Some tests failed"
        exit 1
    fi
}

main "$@"
