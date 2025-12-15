#!/bin/bash
#
# Sentinel PostgreSQL Restore Script
# Restore from backup file
#
# Usage: ./restore-postgres.sh <backup_file>
# Example: ./restore-postgres.sh /var/backups/sentinel/postgres/sentinel_backup_20251215_010000.sql.gz
#

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /var/backups/sentinel/postgres/sentinel_backup_20251215_010000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"
POSTGRES_CONTAINER="sentinel-postgres"
POSTGRES_USER="sentinel"
POSTGRES_DB="sentinel"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "[$(date)] Starting PostgreSQL restore from: $BACKUP_FILE"
echo "WARNING: This will DROP and recreate the database!"
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Stop backend to prevent connections
echo "[$(date)] Stopping backend..."
docker-compose stop backend

# Drop existing database and recreate
echo "[$(date)] Dropping existing database..."
docker exec -t "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"
docker exec -t "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER" -c "CREATE DATABASE ${POSTGRES_DB};"

# Restore from backup
echo "[$(date)] Restoring from backup..."
gunzip -c "$BACKUP_FILE" | docker exec -i "$POSTGRES_CONTAINER" pg_restore \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    --verbose \
    --no-owner \
    --no-acl

if [ $? -eq 0 ]; then
    echo "[$(date)] Restore completed successfully"
    
    # Restart backend
    echo "[$(date)] Starting backend..."
    docker-compose start backend
    
    echo "[$(date)] Restore process completed"
else
    echo "[$(date)] ERROR: Restore failed!"
    exit 1
fi
