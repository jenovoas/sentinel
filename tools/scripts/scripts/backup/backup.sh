#!/bin/bash
#
# Sentinel Backup System - Main Backup Script
#
# Enterprise-grade PostgreSQL backup system with modular architecture,
# comprehensive validation, and multi-destination support.
#
# Features:
#   - Environment-based configuration (no hardcoding)
#   - Structured logging with multiple levels
#   - Integrity validation and checksums
#   - S3/MinIO support for off-site backups
#   - Optional encryption (AES-256)
#   - Webhook notifications (Slack/Discord)
#   - Automatic cleanup of old backups
#
# Usage:
#   ./backup.sh
#
# Configuration:
#   Set environment variables or create .env file in project root
#   See .env.example for available options
#
# Exit Codes:
#   0 - Success
#   1 - Configuration error
#   2 - Backup creation failed
#   3 - Validation failed
#   4 - Upload failed (non-fatal)
#

set -euo pipefail

# ============================================================================
# INITIALIZATION
# ============================================================================

# Get script directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source required modules
source "$SCRIPT_DIR/lib/config.sh"
source "$SCRIPT_DIR/lib/logging.sh"
source "$SCRIPT_DIR/lib/notifications.sh"
source "$SCRIPT_DIR/lib/validation.sh"

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

BACKUP_FILE=""
BACKUP_PATH=""
BACKUP_START_TIME=""
BACKUP_END_TIME=""

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

#
# Generate backup filename
#
# Returns:
#   Backup filename with timestamp
#
generate_backup_filename() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local filename="sentinel_backup_${timestamp}.sql.gz"
    
    if [[ "${ENCRYPT_ENABLED}" == "true" ]]; then
        filename="${filename}.enc"
    fi
    
    echo "$filename"
}

#
# Create backup directory if it doesn't exist
#
# Returns:
#   0 if directory exists or was created, 1 on error
#
ensure_backup_directory() {
    local backup_dir="${BACKUP_DIR}"
    
    # Check if directory exists
    if [[ -d "$backup_dir" ]]; then
        # Check if writable
        if [[ ! -w "$backup_dir" ]]; then
            log_error "Backup directory not writable: $backup_dir"
            log_error "Run: sudo chown -R \$USER:\$USER $backup_dir"
            return 1
        fi
        return 0
    fi
    
    # Try to create directory
    if mkdir -p "$backup_dir" 2>/dev/null; then
        log_success "Created backup directory: $backup_dir"
        return 0
    else
        log_error "Cannot create backup directory: $backup_dir"
        log_error "Run: sudo mkdir -p $backup_dir && sudo chown -R \$USER:\$USER $backup_dir"
        return 1
    fi
}

# ============================================================================
# BACKUP FUNCTIONS
# ============================================================================

#
# Create PostgreSQL backup
#
# Returns:
#   0 on success, 1 on failure
#
create_backup() {
    log_info "Creating PostgreSQL backup..."
    
    local container="${POSTGRES_CONTAINER}"
    local user="${POSTGRES_USER}"
    local db="${POSTGRES_DB}"
    local compression="${BACKUP_COMPRESSION_LEVEL}"
    
    # Generate backup filename
    BACKUP_FILE=$(generate_backup_filename)
    BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
    
    log_debug "Backup file: $BACKUP_FILE"
    log_debug "Backup path: $BACKUP_PATH"
    
    # Create backup based on encryption setting
    if [[ "${ENCRYPT_ENABLED}" == "true" ]]; then
        create_encrypted_backup
    else
        create_unencrypted_backup
    fi
    
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        log_failure "Backup creation failed"
        return 1
    fi
    
    # Get backup size
    local backup_size=$(du -h "$BACKUP_PATH" | cut -f1)
    log_success "Backup created: $BACKUP_FILE ($backup_size)"
    
    return 0
}

#
# Create unencrypted backup
#
create_unencrypted_backup() {
    docker exec -t "${POSTGRES_CONTAINER}" pg_dump \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --format=custom \
        --compress="${BACKUP_COMPRESSION_LEVEL}" \
        2>&1 | gzip > "$BACKUP_PATH"
}

#
# Create encrypted backup
#
create_encrypted_backup() {
    local key_path="${ENCRYPTION_KEY_PATH}"
    
    # Check encryption key exists
    if [[ ! -f "$key_path" ]]; then
        log_error "Encryption key not found: $key_path"
        log_error "Generate with: openssl rand -base64 32 > $key_path"
        return 1
    fi
    
    docker exec -t "${POSTGRES_CONTAINER}" pg_dump \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --format=custom \
        --compress="${BACKUP_COMPRESSION_LEVEL}" \
        2>&1 \
        | gzip \
        | openssl enc -aes-256-cbc -salt -pbkdf2 \
          -pass file:"$key_path" \
        > "$BACKUP_PATH"
}

#
# Validate created backup
#
# Returns:
#   0 if validation passes, 1 if fails
#
validate_created_backup() {
    log_info "Validating backup integrity..."
    
    if validate_backup "$BACKUP_PATH"; then
        # Calculate and save checksum
        local checksum=$(calculate_checksum "$BACKUP_PATH")
        save_checksum "$BACKUP_PATH" "$checksum"
        log_success "Backup validation passed"
        return 0
    else
        log_failure "Backup validation failed"
        return 1
    fi
}

#
# Upload backup to S3
#
# Returns:
#   0 on success, 1 on failure (non-fatal)
#
upload_to_s3() {
    if [[ "${S3_ENABLED}" != "true" ]]; then
        return 0
    fi
    
    log_info "Uploading to S3..."
    
    local bucket="${S3_BUCKET}"
    local storage_class="${S3_STORAGE_CLASS}"
    
    if aws s3 cp "$BACKUP_PATH" "$bucket/" \
        --storage-class "$storage_class" \
        2>&1 | tee -a "${LOG_FILE}"; then
        log_success "S3 upload completed"
        
        # Upload checksum file too
        if [[ -f "${BACKUP_PATH}.sha256" ]]; then
            aws s3 cp "${BACKUP_PATH}.sha256" "$bucket/" \
                --storage-class "$storage_class" \
                2>/dev/null || true
        fi
        
        return 0
    else
        log_warn "S3 upload failed (non-fatal)"
        return 1
    fi
}

#
# Upload backup to MinIO
#
# Returns:
#   0 on success, 1 on failure (non-fatal)
#
upload_to_minio() {
    if [[ "${MINIO_ENABLED}" != "true" ]]; then
        return 0
    fi
    
    log_info "Uploading to MinIO..."
    
    local endpoint="${MINIO_ENDPOINT}"
    local bucket="${MINIO_BUCKET}"
    
    # Configure MinIO client if not already done
    if ! mc alias list | grep -q "^minio"; then
        mc alias set minio "$endpoint" \
            "${MINIO_ACCESS_KEY}" \
            "${MINIO_SECRET_KEY}" \
            2>/dev/null || true
    fi
    
    if mc cp "$BACKUP_PATH" "minio/$bucket/" \
        2>&1 | tee -a "${LOG_FILE}"; then
        log_success "MinIO upload completed"
        
        # Upload checksum file too
        if [[ -f "${BACKUP_PATH}.sha256" ]]; then
            mc cp "${BACKUP_PATH}.sha256" "minio/$bucket/" \
                2>/dev/null || true
        fi
        
        return 0
    else
        log_warn "MinIO upload failed (non-fatal)"
        return 1
    fi
}

#
# Cleanup old backups
#
cleanup_old_backups() {
    log_info "Cleaning up old backups..."
    
    local retention_days="${BACKUP_RETENTION_DAYS}"
    local backup_dir="${BACKUP_DIR}"
    
    # Local cleanup
    local deleted_count=$(find "$backup_dir" \
        -name "sentinel_backup_*.sql.gz*" \
        -mtime +${retention_days} \
        -delete -print | wc -l)
    
    log_info "Deleted $deleted_count old local backup(s)"
    
    # S3 cleanup if enabled
    if [[ "${S3_ENABLED}" == "true" ]]; then
        cleanup_s3_backups
    fi
}

#
# Cleanup old S3 backups
#
cleanup_s3_backups() {
    local bucket="${S3_BUCKET}"
    local retention_days="${BACKUP_RETENTION_DAYS}"
    local cutoff_date=$(date -d "${retention_days} days ago" +%Y-%m-%d 2>/dev/null || date -v-${retention_days}d +%Y-%m-%d)
    
    log_debug "Cleaning S3 backups older than $cutoff_date"
    
    aws s3 ls "$bucket/" \
        | awk '{print $4}' \
        | while read file; do
            # Extract date from filename (YYYYMMDD)
            local file_date=$(echo "$file" | grep -oP '\d{8}' | head -1)
            if [[ -n "$file_date" ]]; then
                local file_date_formatted=$(date -d "${file_date:0:4}-${file_date:4:2}-${file_date:6:2}" +%Y-%m-%d 2>/dev/null || echo "")
                if [[ -n "$file_date_formatted" ]] && [[ "$file_date_formatted" < "$cutoff_date" ]]; then
                    aws s3 rm "${bucket}/${file}" 2>/dev/null || true
                    log_debug "Deleted old S3 backup: $file"
                fi
            fi
        done
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    # Record start time
    BACKUP_START_TIME=$(date +%s)
    
    log_section "Sentinel Backup System"
    log_info "Starting backup process..."
    
    # Load configuration
    if ! load_config; then
        log_failure "Configuration loading failed"
        notify_error "Backup failed: Configuration error"
        exit 1
    fi
    
    log_debug "Configuration loaded successfully"
    
    # Ensure backup directory exists
    if ! ensure_backup_directory; then
        log_failure "Cannot access backup directory"
        notify_error "Backup failed: Directory access error"
        exit 1
    fi
    
    # Create backup
    if ! create_backup; then
        log_failure "Backup creation failed"
        notify_error "Backup failed: Creation error"
        exit 2
    fi
    
    # Validate backup
    if ! validate_created_backup; then
        log_failure "Backup validation failed"
        notify_error "Backup failed: Validation error"
        exit 3
    fi
    
    # Upload to remote storage (non-fatal)
    upload_to_s3 || log_warn "S3 upload skipped or failed"
    upload_to_minio || log_warn "MinIO upload skipped or failed"
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Calculate duration
    BACKUP_END_TIME=$(date +%s)
    local duration=$((BACKUP_END_TIME - BACKUP_START_TIME))
    
    # Final summary
    log_section "Backup Summary"
    log_info "Backup file: $BACKUP_FILE"
    log_info "Backup size: $(du -h "$BACKUP_PATH" | cut -f1)"
    log_info "Duration: ${duration}s"
    log_info "Total backups: $(ls -1 "$BACKUP_DIR"/sentinel_backup_*.sql.gz* 2>/dev/null | wc -l)"
    log_success "Backup process completed successfully"
    
    # Send success notification
    notify_success "Backup completed: $BACKUP_FILE (${duration}s)"
    
    exit 0
}

# Run main function
main "$@"
