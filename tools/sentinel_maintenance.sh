#!/bin/bash
# Sentinel Cortex Maintenance Script
# To be run via cron (e.g., daily)

BACKUP_DIR="/var/backups/sentinel"
SHM_PATH="/var/run/sentinel/truthsync_shm"
LOG_DIR="/var/log/sentinel"
RETENTION_DAYS=7

echo "[$(date)] 🔧 Starting Sentinel Maintenance..."

# 1. Backup TruthSync SHM (Snapshot of system consciousness)
mkdir -p "$BACKUP_DIR"
if [ -f "$SHM_PATH" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    cp "$SHM_PATH" "$BACKUP_DIR/truthsync_shm_$TIMESTAMP.bin"
    echo "   ✅ Backup created: truthsync_shm_$TIMESTAMP.bin"
    
    # Compress
    gzip "$BACKUP_DIR/truthsync_shm_$TIMESTAMP.bin"
else
    echo "   ⚠️ SHM file not found. Skipping backup."
fi

# 2. Rotate Logs
if [ -d "$LOG_DIR" ]; then
    echo "   🧹 Cleaning old logs..."
    find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.bin.gz" -type f -mtime +$RETENTION_DAYS -delete
fi

echo "[$(date)] ✅ Maintenance Complete."
