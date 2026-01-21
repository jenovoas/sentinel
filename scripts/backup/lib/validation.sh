#!/bin/bash
#
# Sentinel Backup System - Validation Module
#
# This module provides backup validation functionality including integrity checks,
# checksum verification, and backup file validation.
#
# Usage:
#   source "$(dirname "$0")/lib/validation.sh"
#   validate_backup_integrity "/path/to/backup.sql.gz"
#   verify_backup_checksum "/path/to/backup.sql.gz"
#
# Validation Types:
#   - Integrity check (gunzip -t)
#   - Checksum verification (SHA256)
#   - File size validation
#   - Backup age validation
#

set -euo pipefail

# ============================================================================
# CONSTANTS
# ============================================================================

readonly MIN_BACKUP_SIZE=1024  # Minimum backup size in bytes (1KB)
readonly MAX_BACKUP_AGE_HOURS=24  # Maximum backup age in hours

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

#
# Validate backup file integrity
#
# Checks if the backup file is a valid gzip file and can be decompressed.
#
# Args:
#   $1 - Path to backup file
#
# Returns:
#   0 if valid, 1 if invalid
#
validate_backup_integrity() {
    local backup_file="$1"
    
    # Check if file exists
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Check if file is encrypted
    if [[ "$backup_file" =~ \.enc$ ]]; then
        validate_encrypted_backup_integrity "$backup_file"
        return $?
    fi
    
    # Validate gzip integrity
    if gunzip -t "$backup_file" 2>/dev/null; then
        log_debug "Backup integrity check passed: $backup_file"
        return 0
    else
        log_error "Backup integrity check failed: $backup_file"
        return 1
    fi
}

#
# Validate encrypted backup file integrity
#
# Checks if the encrypted backup file can be decrypted and decompressed.
#
# Args:
#   $1 - Path to encrypted backup file
#
# Returns:
#   0 if valid, 1 if invalid
#
validate_encrypted_backup_integrity() {
    local backup_file="$1"
    local encryption_key="${ENCRYPTION_KEY_PATH:-}"
    
    # Check if encryption key exists
    if [[ ! -f "$encryption_key" ]]; then
        log_error "Encryption key not found: $encryption_key"
        return 1
    fi
    
    # Decrypt and validate
    if openssl enc -aes-256-cbc -d -pbkdf2 \
        -pass file:"$encryption_key" \
        -in "$backup_file" \
        2>/dev/null | gunzip -t 2>/dev/null; then
        log_debug "Encrypted backup integrity check passed: $backup_file"
        return 0
    else
        log_error "Encrypted backup integrity check failed: $backup_file"
        return 1
    fi
}

#
# Calculate checksum for backup file
#
# Args:
#   $1 - Path to backup file
#
# Returns:
#   SHA256 checksum string
#
calculate_checksum() {
    local backup_file="$1"
    
    if [[ ! -f "$backup_file" ]]; then
        echo ""
        return 1
    fi
    
    # Calculate SHA256 checksum
    sha256sum "$backup_file" | awk '{print $1}'
}

#
# Save checksum to file
#
# Args:
#   $1 - Path to backup file
#   $2 - Checksum string
#
save_checksum() {
    local backup_file="$1"
    local checksum="$2"
    local checksum_file="${backup_file}.sha256"
    
    echo "$checksum  $(basename "$backup_file")" > "$checksum_file"
    log_debug "Checksum saved: $checksum_file"
}

#
# Verify backup checksum
#
# Args:
#   $1 - Path to backup file
#
# Returns:
#   0 if checksum matches, 1 if mismatch or checksum file not found
#
verify_backup_checksum() {
    local backup_file="$1"
    local checksum_file="${backup_file}.sha256"
    
    # Check if checksum file exists
    if [[ ! -f "$checksum_file" ]]; then
        log_warn "Checksum file not found: $checksum_file"
        return 1
    fi
    
    # Calculate current checksum
    local current_checksum=$(calculate_checksum "$backup_file")
    
    # Read saved checksum
    local saved_checksum=$(awk '{print $1}' "$checksum_file")
    
    # Compare checksums
    if [[ "$current_checksum" == "$saved_checksum" ]]; then
        log_debug "Checksum verification passed: $backup_file"
        return 0
    else
        log_error "Checksum verification failed: $backup_file"
        log_error "Expected: $saved_checksum"
        log_error "Got: $current_checksum"
        return 1
    fi
}

#
# Validate backup file size
#
# Checks if backup file size is within acceptable range.
#
# Args:
#   $1 - Path to backup file
#
# Returns:
#   0 if size is valid, 1 if too small
#
validate_backup_size() {
    local backup_file="$1"
    local min_size="${MIN_BACKUP_SIZE}"
    
    # Get file size
    local file_size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file" 2>/dev/null)
    
    if [[ $file_size -lt $min_size ]]; then
        log_error "Backup file too small: $file_size bytes (minimum: $min_size bytes)"
        return 1
    fi
    
    log_debug "Backup size validation passed: $file_size bytes"
    return 0
}

#
# Validate backup age
#
# Checks if backup file is not too old.
#
# Args:
#   $1 - Path to backup file
#
# Returns:
#   0 if age is acceptable, 1 if too old
#
validate_backup_age() {
    local backup_file="$1"
    local max_age_hours="${MAX_BACKUP_AGE_HOURS}"
    
    # Get file modification time
    local file_mtime=$(stat -f%m "$backup_file" 2>/dev/null || stat -c%Y "$backup_file" 2>/dev/null)
    local current_time=$(date +%s)
    local age_seconds=$((current_time - file_mtime))
    local age_hours=$((age_seconds / 3600))
    
    if [[ $age_hours -gt $max_age_hours ]]; then
        log_warn "Backup file is old: $age_hours hours (maximum: $max_age_hours hours)"
        return 1
    fi
    
    log_debug "Backup age validation passed: $age_hours hours"
    return 0
}

#
# Comprehensive backup validation
#
# Runs all validation checks on a backup file.
#
# Args:
#   $1 - Path to backup file
#
# Returns:
#   0 if all checks pass, 1 if any check fails
#
validate_backup() {
    local backup_file="$1"
    local errors=0
    
    log_info "Validating backup: $(basename "$backup_file")"
    
    # Check file exists
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Validate integrity
    if ! validate_backup_integrity "$backup_file"; then
        ((errors++))
    fi
    
    # Validate size
    if ! validate_backup_size "$backup_file"; then
        ((errors++))
    fi
    
    # Verify checksum if available
    if ! verify_backup_checksum "$backup_file"; then
        log_warn "Checksum verification skipped or failed"
    fi
    
    # Report results
    if [[ $errors -eq 0 ]]; then
        log_success "Backup validation passed"
        return 0
    else
        log_failure "Backup validation failed with $errors error(s)"
        return 1
    fi
}

# ============================================================================
# EXPORTS
# ============================================================================

# Export validation functions
export -f validate_backup_integrity
export -f validate_encrypted_backup_integrity
export -f calculate_checksum
export -f save_checksum
export -f verify_backup_checksum
export -f validate_backup_size
export -f validate_backup_age
export -f validate_backup
