#!/bin/bash
# Sentinel Cortex Maintenance Script
# To be run via cron (e.g., daily) or as a systemd service with watchdog.

BACKUP_DIR="/var/backups/sentinel"
SHM_PATH="/var/run/sentinel/truthsync_shm"
LOG_DIR="/var/log/sentinel"
RETENTION_DAYS=7
mkdir -p "$LOG_DIR"
# Ensure health log file exists
touch "$LOG_DIR/health.log"

# Function to perform all maintenance tasks
run_maintenance() {
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

    # 2. Rotate Logs and clean old backups
    if [ -d "$LOG_DIR" ]; then
        echo "   🧹 Cleaning old logs..."
        find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete
    fi
    if [ -d "$BACKUP_DIR" ]; then
        echo "   🧹 Cleaning old backups..."
        find "$BACKUP_DIR" -name "*.bin.gz" -type f -mtime +$RETENTION_DAYS -delete
    fi

    echo "[$(date)] ✅ Maintenance Complete."
}

# Main script logic
if [[ "$1" == "--monitor" ]]; then
    echo "[$(date)] 🚀 Starting Sentinel Maintenance in monitor mode..."
    # Notify systemd that the service is ready
    if [ -n "$NOTIFY_SOCKET" ]; then systemd-notify --ready; fi

    while true; do
        run_maintenance
# Health check – capture Sentinel status
if command -v sctl >/dev/null 2>&1; then
  sctl status --json >> "$LOG_DIR/health.log" 2>&1 || true
fi
        # Notify systemd watchdog that the service is alive and performing maintenance
        if [ -n "$NOTIFY_SOCKET" ]; then systemd-notify --status="Performing periodic maintenance." WATCHDOG=1; fi
        sleep "$WATCHDOG_INTERVAL_SECONDS"
    done
else
    # Run maintenance once if not in monitor mode (e.g., Type=oneshot systemd service or cron)
    # Guard systemd-notify calls to ensure they only run when systemd is active
    if command -v systemd-notify &> /dev/null && [ -n "$NOTIFY_SOCKET" ]; then
        systemd-notify --ready --status="Starting one-shot maintenance."
    fi

    run_maintenance

    if command -v systemd-notify &> /dev/null && [ -n "$NOTIFY_SOCKET" ]; then
        systemd-notify --status="One-shot maintenance complete."
    fi
fi
