#!/bin/bash
#
# Sentinel PostgreSQL Backup Script (Enhanced)
# Features: S3 sync, integrity check, encryption, alerts
#
# Usage: ./backup-postgres.sh
# Cron: 0 */6 * * * /path/to/backup-postgres.sh >> /var/log/sentinel-backup.log 2>&1
#

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

# Backup settings
BACKUP_DIR="/var/backups/sentinel/postgres"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="sentinel_backup_${TIMESTAMP}.sql.gz"

# PostgreSQL settings
POSTGRES_CONTAINER="sentinel-postgres"
POSTGRES_USER="sentinel_user"
POSTGRES_DB="sentinel_db"

# S3/MinIO settings (set S3_ENABLED=false to disable)
S3_ENABLED=false
S3_BUCKET="s3://sentinel-backups/postgres"
S3_STORAGE_CLASS="STANDARD_IA"  # Options: STANDARD, STANDARD_IA, GLACIER

# MinIO settings (alternative to S3)
MINIO_ENABLED=false
MINIO_ALIAS="minio"
MINIO_BUCKET="sentinel-backups/postgres"

# Encryption settings (set ENCRYPT_ENABLED=false to disable)
ENCRYPT_ENABLED=false
ENCRYPTION_KEY="/etc/sentinel/backup.key"

# Webhook for alerts (leave empty to disable)
WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

send_alert() {
    local message="$1"
    local emoji="$2"
    
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST "$WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"${emoji} ${message}\"}" \
            > /dev/null 2>&1 || true
    fi
}

# ============================================================================
# MAIN BACKUP PROCESS
# ============================================================================

log "Starting PostgreSQL backup..."

# Create backup directory (check if writable first)
if [ ! -d "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR" 2>/dev/null || {
        log "ERROR: Cannot create backup directory: $BACKUP_DIR"
        log "Please run: sudo mkdir -p $BACKUP_DIR && sudo chown -R \$USER:\$USER /var/backups/sentinel"
        send_alert "Sentinel backup FAILED: Cannot create backup directory" "🚨"
        exit 1
    }
fi

# Check if directory is writable
if [ ! -w "$BACKUP_DIR" ]; then
    log "ERROR: Backup directory not writable: $BACKUP_DIR"
    log "Please run: sudo chown -R \$USER:\$USER /var/backups/sentinel"
    send_alert "Sentinel backup FAILED: Backup directory not writable" "🚨"
    exit 1
fi

# Perform backup
if [ "$ENCRYPT_ENABLED" = true ]; then
    log "Creating encrypted backup..."
    
    # Check if encryption key exists
    if [ ! -f "$ENCRYPTION_KEY" ]; then
        log "ERROR: Encryption key not found at $ENCRYPTION_KEY"
        log "Generate key with: openssl rand -base64 32 > $ENCRYPTION_KEY"
        send_alert "Sentinel backup FAILED: Encryption key not found" "🚨"
        exit 1
    fi
    
    docker exec -t "$POSTGRES_CONTAINER" pg_dump \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --format=custom \
        --compress=9 \
        --verbose \
        2>&1 | grep -v "^$" \
        | gzip \
        | openssl enc -aes-256-cbc -salt -pbkdf2 \
          -pass file:"$ENCRYPTION_KEY" \
        > "${BACKUP_DIR}/${BACKUP_FILE}.enc"
    
    BACKUP_FILE="${BACKUP_FILE}.enc"
else
    log "Creating unencrypted backup..."
    
    docker exec -t "$POSTGRES_CONTAINER" pg_dump \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --format=custom \
        --compress=9 \
        --verbose \
        2>&1 | grep -v "^$" \
        | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"
fi

# Check if backup was successful
if [ $? -ne 0 ]; then
    log "ERROR: Backup failed!"
    send_alert "Sentinel backup FAILED!" "🚨"
    exit 1
fi

BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
log "Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

# ============================================================================
# INTEGRITY VERIFICATION
# ============================================================================

log "Verifying backup integrity..."

if [ "$ENCRYPT_ENABLED" = true ]; then
    # Verify encrypted backup
    openssl enc -aes-256-cbc -d -pbkdf2 \
        -pass file:"$ENCRYPTION_KEY" \
        -in "${BACKUP_DIR}/${BACKUP_FILE}" \
        2>/dev/null | gunzip -t 2>/dev/null
else
    # Verify unencrypted backup
    gunzip -t "${BACKUP_DIR}/${BACKUP_FILE}" 2>/dev/null
fi

if [ $? -eq 0 ]; then
    log "Backup integrity verified ✓"
else
    log "ERROR: Backup corrupted!"
    send_alert "Sentinel backup CORRUPTED! File: ${BACKUP_FILE}" "🚨"
    exit 1
fi

# ============================================================================
# S3/MINIO UPLOAD
# ============================================================================

if [ "$S3_ENABLED" = true ]; then
    log "Uploading to S3..."
    
    aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" \
        "$S3_BUCKET/" \
        --storage-class "$S3_STORAGE_CLASS" \
        2>&1
    
    if [ $? -eq 0 ]; then
        log "S3 upload successful ✓"
    else
        log "WARNING: S3 upload failed"
        send_alert "Sentinel S3 backup upload FAILED" "⚠️"
    fi
fi

if [ "$MINIO_ENABLED" = true ]; then
    log "Uploading to MinIO..."
    
    mc cp "${BACKUP_DIR}/${BACKUP_FILE}" \
        "${MINIO_ALIAS}/${MINIO_BUCKET}/" \
        2>&1
    
    if [ $? -eq 0 ]; then
        log "MinIO upload successful ✓"
    else
        log "WARNING: MinIO upload failed"
        send_alert "Sentinel MinIO backup upload FAILED" "⚠️"
    fi
fi

# ============================================================================
# CLEANUP OLD BACKUPS
# ============================================================================

log "Cleaning up backups older than ${RETENTION_DAYS} days..."

# Local cleanup
DELETED_COUNT=$(find "$BACKUP_DIR" -name "sentinel_backup_*.sql.gz*" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
log "Deleted ${DELETED_COUNT} old local backup(s)"

# S3 cleanup (if enabled)
if [ "$S3_ENABLED" = true ]; then
    CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d)
    aws s3 ls "$S3_BUCKET/" \
        | awk '{print $4}' \
        | while read file; do
            FILE_DATE=$(echo "$file" | grep -oP '\d{8}' | head -1)
            if [ -n "$FILE_DATE" ]; then
                FILE_DATE_FORMATTED=$(date -d "${FILE_DATE:0:4}-${FILE_DATE:4:2}-${FILE_DATE:6:2}" +%Y-%m-%d)
                if [[ "$FILE_DATE_FORMATTED" < "$CUTOFF_DATE" ]]; then
                    aws s3 rm "${S3_BUCKET}/${file}"
                    log "Deleted old S3 backup: $file"
                fi
            fi
        done
fi

# ============================================================================
# SUMMARY
# ============================================================================

log "Current local backups:"
ls -lh "$BACKUP_DIR" | tail -n +2

TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/sentinel_backup_*.sql.gz* 2>/dev/null | wc -l)

log "Summary: ${BACKUP_COUNT} backups, ${TOTAL_SIZE} total"
log "Backup process completed ✓"

# Success notification
send_alert "Sentinel backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})" "✅"

exit 0
