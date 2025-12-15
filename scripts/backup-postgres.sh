#!/bin/bash
#
# Sentinel PostgreSQL Backup Script
# Automated backup with retention policy
#
# Usage: ./backup-postgres.sh
# Cron: 0 */6 * * * /path/to/backup-postgres.sh
#

set -e

# Configuration
BACKUP_DIR="/var/backups/sentinel/postgres"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="sentinel_backup_${TIMESTAMP}.sql.gz"
POSTGRES_CONTAINER="sentinel-postgres"
POSTGRES_USER="sentinel"
POSTGRES_DB="sentinel"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting PostgreSQL backup..."

# Perform backup
docker exec -t "$POSTGRES_CONTAINER" pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --format=custom \
    --compress=9 \
    --verbose \
    | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Check if backup was successful
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    echo "[$(date)] Backup completed successfully: ${BACKUP_FILE} (${BACKUP_SIZE})"
    
    # Optional: Upload to S3/MinIO
    # aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" s3://sentinel-backups/postgres/
    
    # Optional: Send success notification
    # curl -X POST https://your-webhook-url -d "Backup completed: ${BACKUP_FILE}"
else
    echo "[$(date)] ERROR: Backup failed!"
    # Send failure alert
    # curl -X POST https://your-webhook-url -d "ALERT: Backup failed!"
    exit 1
fi

# Cleanup old backups (keep last N days)
echo "[$(date)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "sentinel_backup_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# List current backups
echo "[$(date)] Current backups:"
ls -lh "$BACKUP_DIR"

echo "[$(date)] Backup process completed"
