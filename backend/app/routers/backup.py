"""
Backup System API Router

Provides RESTful endpoints for backup monitoring, management, and administration.

Endpoints:
    - GET  /api/v1/backup/status   - Overall backup system status and metrics
    - GET  /api/v1/backup/history  - Paginated backup history
    - POST /api/v1/backup/trigger  - Manually trigger a backup
    - GET  /api/v1/backup/logs     - Recent backup logs
    - GET  /api/v1/backup/config   - Current backup configuration
    - GET  /api/v1/backup/health   - Health check endpoint

Author: Sentinel Team
Created: 2025-12-15
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import os
import glob
import subprocess
import json
from functools import lru_cache
import time

router = APIRouter(prefix="/api/v1/backup", tags=["backup"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class BackupFile(BaseModel):
    """Model for a single backup file"""
    filename: str = Field(..., description="Backup filename")
    size_bytes: int = Field(..., description="File size in bytes")
    size_mb: float = Field(..., description="File size in MB")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    age_hours: float = Field(..., description="Age in hours")
    has_checksum: bool = Field(..., description="Whether SHA256 checksum exists")
    is_encrypted: bool = Field(False, description="Whether backup is encrypted")


class BackupMetrics(BaseModel):
    """Aggregated backup metrics"""
    total_backups: int = Field(..., description="Total number of backups")
    total_size_mb: float = Field(..., description="Total size of all backups in MB")
    oldest_backup_age_hours: float = Field(..., description="Age of oldest backup in hours")
    newest_backup_age_hours: float = Field(..., description="Age of newest backup in hours")
    average_size_mb: float = Field(..., description="Average backup size in MB")
    success_rate_24h: float = Field(..., description="Success rate in last 24 hours (0-100)")


class BackupConfig(BaseModel):
    """Current backup configuration"""
    backup_dir: str = Field(..., description="Backup directory path")
    retention_days: int = Field(..., description="Retention period in days")
    s3_enabled: bool = Field(..., description="Whether S3 upload is enabled")
    minio_enabled: bool = Field(..., description="Whether MinIO upload is enabled")
    encryption_enabled: bool = Field(..., description="Whether encryption is enabled")
    webhook_enabled: bool = Field(..., description="Whether webhook notifications are enabled")


class LastBackup(BaseModel):
    """Information about the last backup"""
    status: str = Field(..., description="Status: success, failed, or unknown")
    time: Optional[str] = Field(None, description="Timestamp of last backup")
    age_hours: Optional[float] = Field(None, description="Age in hours")
    duration_seconds: Optional[int] = Field(None, description="Duration in seconds")


class BackupStatus(BaseModel):
    """Complete backup system status"""
    health: str = Field(..., description="Overall health: healthy, warning, or critical")
    last_backup: LastBackup = Field(..., description="Last backup information")
    metrics: BackupMetrics = Field(..., description="Aggregated metrics")
    backups: List[BackupFile] = Field(..., description="List of recent backups")
    config: BackupConfig = Field(..., description="Current configuration")


class BackupTriggerResponse(BaseModel):
    """Response from backup trigger"""
    status: str = Field(..., description="Trigger status: success or failed")
    exit_code: int = Field(..., description="Exit code from backup script")
    message: str = Field(..., description="Status message")
    output: Optional[str] = Field(None, description="Last 500 chars of output")


class BackupLogs(BaseModel):
    """Backup logs response"""
    logs: List[str] = Field(..., description="List of log lines")
    total_lines: int = Field(..., description="Total number of lines in log file")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_backup_dir() -> str:
    """Get backup directory from environment or use default"""
    return os.getenv("BACKUP_DIR", "/var/backups/sentinel/postgres")


def get_log_file() -> str:
    """Get log file path from environment or use default"""
    return os.getenv("LOG_FILE", "/var/log/sentinel-backup.log")


def parse_backup_filename(filename: str) -> Optional[datetime]:
    """
    Parse timestamp from backup filename
    
    Args:
        filename: Backup filename (e.g., sentinel_backup_20251215_163138.sql.gz)
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Extract timestamp: sentinel_backup_YYYYMMDD_HHMMSS.sql.gz
        parts = filename.replace(".sql.gz", "").replace(".enc", "").split("_")
        if len(parts) >= 4:
            date_str = parts[2]  # YYYYMMDD
            time_str = parts[3]  # HHMMSS
            timestamp_str = f"{date_str}_{time_str}"
            return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
    except Exception:
        pass
    return None


@lru_cache(maxsize=1)
def get_cached_status(cache_key: int) -> Dict[str, Any]:
    """
    Get cached backup status (cached for 30 seconds)
    
    Args:
        cache_key: Current time // 30 (changes every 30 seconds)
        
    Returns:
        Dictionary with backup status data
    """
    backup_dir = get_backup_dir()
    log_file = get_log_file()
    
    # Get list of backups
    backups = []
    if os.path.exists(backup_dir):
        backup_files = sorted(
            glob.glob(f"{backup_dir}/sentinel_backup_*.sql.gz*"),
            key=os.path.getmtime,
            reverse=True
        )
        
        for backup_file in backup_files[:20]:  # Last 20 backups
            # Skip checksum files
            if backup_file.endswith(".sha256"):
                continue
                
            try:
                stat = os.stat(backup_file)
                filename = os.path.basename(backup_file)
                
                backups.append({
                    "filename": filename,
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "age_hours": round((time.time() - stat.st_mtime) / 3600, 1),
                    "has_checksum": os.path.exists(f"{backup_file}.sha256"),
                    "is_encrypted": filename.endswith(".enc")
                })
            except Exception as e:
                print(f"Error processing backup file {backup_file}: {e}")
                continue
    
    # Parse last backup from log
    last_backup_status = "unknown"
    last_backup_time = None
    last_backup_duration = None
    success_count_24h = 0
    total_count_24h = 0
    
    if os.path.exists(log_file):
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            with open(log_file, 'r') as f:
                lines = f.readlines()
                
                for line in reversed(lines[-500:]):  # Last 500 lines
                    # Extract timestamp
                    if line.startswith("["):
                        try:
                            timestamp_str = line[1:20]
                            log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            
                            # Count successes and failures in last 24h
                            if log_time >= cutoff_time:
                                if "Backup process completed successfully" in line:
                                    success_count_24h += 1
                                    total_count_24h += 1
                                elif "Backup failed" in line or "ERROR" in line and "Backup" in line:
                                    total_count_24h += 1
                            
                            # Get last backup info
                            if last_backup_status == "unknown":
                                if "Backup process completed successfully" in line:
                                    last_backup_status = "success"
                                    last_backup_time = timestamp_str
                                elif "Backup failed" in line or "ERROR" in line:
                                    last_backup_status = "failed"
                                    last_backup_time = timestamp_str
                        except Exception:
                            continue
        except Exception as e:
            print(f"Error reading log file: {e}")
    
    # Calculate metrics
    total_backups = len(backups)
    total_size_mb = sum(b["size_mb"] for b in backups)
    oldest_backup_age = max([b["age_hours"] for b in backups]) if backups else 0
    newest_backup_age = min([b["age_hours"] for b in backups]) if backups else 0
    success_rate_24h = (success_count_24h / total_count_24h * 100) if total_count_24h > 0 else 100.0
    
    # Determine health status
    health = "healthy"
    if newest_backup_age > 24:
        health = "warning"  # No backup in 24 hours
    if newest_backup_age > 48:
        health = "critical"  # No backup in 48 hours
    if last_backup_status == "failed":
        health = "critical"
    
    return {
        "health": health,
        "last_backup": {
            "status": last_backup_status,
            "time": last_backup_time,
            "age_hours": newest_backup_age if backups else None,
            "duration_seconds": last_backup_duration
        },
        "metrics": {
            "total_backups": total_backups,
            "total_size_mb": round(total_size_mb, 2),
            "oldest_backup_age_hours": round(oldest_backup_age, 1),
            "newest_backup_age_hours": round(newest_backup_age, 1),
            "average_size_mb": round(total_size_mb / total_backups, 2) if total_backups > 0 else 0,
            "success_rate_24h": round(success_rate_24h, 1)
        },
        "backups": backups,
        "config": {
            "backup_dir": backup_dir,
            "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "7")),
            "s3_enabled": os.getenv("S3_ENABLED", "false").lower() == "true",
            "minio_enabled": os.getenv("MINIO_ENABLED", "false").lower() == "true",
            "encryption_enabled": os.getenv("ENCRYPT_ENABLED", "false").lower() == "true",
            "webhook_enabled": os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
        }
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/status", response_model=BackupStatus)
async def get_backup_status():
    """
    Get current backup system status and metrics
    
    Returns comprehensive backup system information including:
    - Overall health status
    - Last backup information
    - Aggregated metrics
    - Recent backup files
    - Current configuration
    
    Cached for 30 seconds to optimize performance.
    """
    try:
        # Cache key changes every 30 seconds
        cache_key = int(time.time() // 30)
        status_data = get_cached_status(cache_key)
        return BackupStatus(**status_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get backup status: {str(e)}"
        )


@router.get("/history", response_model=List[BackupFile])
async def get_backup_history(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of backups to return"),
    offset: int = Query(default=0, ge=0, description="Number of backups to skip")
):
    """
    Get paginated backup history
    
    Args:
        limit: Maximum number of backups to return (1-100)
        offset: Number of backups to skip for pagination
        
    Returns:
        List of backup files with metadata
    """
    try:
        backup_dir = get_backup_dir()
        
        if not os.path.exists(backup_dir):
            return []
        
        backup_files = sorted(
            glob.glob(f"{backup_dir}/sentinel_backup_*.sql.gz*"),
            key=os.path.getmtime,
            reverse=True
        )
        
        backups = []
        for backup_file in backup_files[offset:offset+limit]:
            # Skip checksum files
            if backup_file.endswith(".sha256"):
                continue
                
            try:
                stat = os.stat(backup_file)
                filename = os.path.basename(backup_file)
                
                backups.append(BackupFile(
                    filename=filename,
                    size_bytes=stat.st_size,
                    size_mb=round(stat.st_size / 1024 / 1024, 2),
                    created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    age_hours=round((time.time() - stat.st_mtime) / 3600, 1),
                    has_checksum=os.path.exists(f"{backup_file}.sha256"),
                    is_encrypted=filename.endswith(".enc")
                ))
            except Exception as e:
                print(f"Error processing backup file {backup_file}: {e}")
                continue
        
        return backups
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get backup history: {str(e)}"
        )


@router.post("/trigger", response_model=BackupTriggerResponse)
async def trigger_backup():
    """
    Manually trigger a backup
    
    Executes the backup script and returns the result.
    This operation may take several seconds to complete.
    
    Returns:
        Backup trigger response with status and output
    """
    try:
        # Get project root (assuming backend is in backend/ directory)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        backup_script = os.path.join(project_root, "scripts", "backup", "backup.sh")
        
        if not os.path.exists(backup_script):
            raise HTTPException(
                status_code=404,
                detail=f"Backup script not found: {backup_script}"
            )
        
        # Execute backup script
        result = subprocess.run(
            [backup_script],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=project_root
        )
        
        status = "success" if result.returncode == 0 else "failed"
        message = "Backup completed successfully" if result.returncode == 0 else "Backup failed"
        
        # Clear cache to force refresh
        get_cached_status.cache_clear()
        
        return BackupTriggerResponse(
            status=status,
            exit_code=result.returncode,
            message=message,
            output=result.stdout[-500:] if result.stdout else result.stderr[-500:]
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Backup operation timed out (exceeded 5 minutes)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger backup: {str(e)}"
        )


@router.get("/logs", response_model=BackupLogs)
async def get_backup_logs(
    lines: int = Query(default=100, ge=1, le=1000, description="Number of log lines to return")
):
    """
    Get recent backup logs
    
    Args:
        lines: Number of recent log lines to return (1-1000)
        
    Returns:
        Recent log lines and total line count
    """
    try:
        log_file = get_log_file()
        
        if not os.path.exists(log_file):
            return BackupLogs(logs=[], total_lines=0)
        
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]
            
        return BackupLogs(
            logs=[line.strip() for line in recent_lines],
            total_lines=len(all_lines)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read backup logs: {str(e)}"
        )


@router.get("/config", response_model=BackupConfig)
async def get_backup_config():
    """
    Get current backup configuration
    
    Returns:
        Current backup system configuration
    """
    try:
        return BackupConfig(
            backup_dir=get_backup_dir(),
            retention_days=int(os.getenv("BACKUP_RETENTION_DAYS", "7")),
            s3_enabled=os.getenv("S3_ENABLED", "false").lower() == "true",
            minio_enabled=os.getenv("MINIO_ENABLED", "false").lower() == "true",
            encryption_enabled=os.getenv("ENCRYPT_ENABLED", "false").lower() == "true",
            webhook_enabled=os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get backup configuration: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Simple health status
    """
    return {"status": "healthy", "service": "backup-api"}
