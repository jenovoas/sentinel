# 📚 Backup API Documentation

## Overview

The Backup API provides RESTful endpoints for monitoring, managing, and administering the Sentinel backup system. Built with FastAPI and designed for high performance with caching and async operations.

## Base URL

```
http://localhost:8000/api/v1/backup
```

## Authentication

Currently no authentication required. **TODO**: Add JWT authentication before production deployment.

## Endpoints

### 1. Get Backup Status

**GET** `/status`

Returns comprehensive backup system status including health, metrics, and recent backups.

**Response** (200 OK):
```json
{
  "health": "healthy",
  "last_backup": {
    "status": "success",
    "time": "2025-12-15 16:31:38",
    "age_hours": 0.5,
    "duration_seconds": null
  },
  "metrics": {
    "total_backups": 4,
    "total_size_mb": 950.0,
    "oldest_backup_age_hours": 24.5,
    "newest_backup_age_hours": 0.5,
    "average_size_mb": 237.5,
    "success_rate_24h": 100.0
  },
  "backups": [
    {
      "filename": "sentinel_backup_20251215_163628.sql.gz",
      "size_bytes": 241664,
      "size_mb": 0.23,
      "created_at": "2025-12-15T16:36:28",
      "age_hours": 0.5,
      "has_checksum": true,
      "is_encrypted": false
    }
  ],
  "config": {
    "backup_dir": "/var/backups/sentinel/postgres",
    "retention_days": 7,
    "s3_enabled": false,
    "minio_enabled": false,
    "encryption_enabled": false,
    "webhook_enabled": false
  }
}
```

**Health Status**:
- `healthy`: Last backup < 24 hours ago, no failures
- `warning`: Last backup 24-48 hours ago
- `critical`: Last backup > 48 hours ago OR last backup failed

**Caching**: Response cached for 30 seconds for performance.

---

### 2. Get Backup History

**GET** `/history?limit=50&offset=0`

Returns paginated list of backup files with metadata.

**Query Parameters**:
- `limit` (int, optional): Maximum backups to return (1-100, default: 50)
- `offset` (int, optional): Number of backups to skip (default: 0)

**Response** (200 OK):
```json
[
  {
    "filename": "sentinel_backup_20251215_163628.sql.gz",
    "size_bytes": 241664,
    "size_mb": 0.23,
    "created_at": "2025-12-15T16:36:28",
    "age_hours": 0.5,
    "has_checksum": true,
    "is_encrypted": false
  }
]
```

**Error Responses**:
- `422`: Invalid query parameters

---

### 3. Trigger Manual Backup

**POST** `/trigger`

Manually triggers a backup execution. This operation may take several seconds.

**Request**: No body required

**Response** (200 OK):
```json
{
  "status": "success",
  "exit_code": 0,
  "message": "Backup completed successfully",
  "output": "[2025-12-15 16:40:00] [INFO] ✓ Backup process completed successfully"
}
```

**Error Responses**:
- `404`: Backup script not found
- `408`: Backup timeout (>5 minutes)
- `500`: Backup execution failed

**Note**: Clears status cache to force immediate refresh.

---

### 4. Get Backup Logs

**GET** `/logs?lines=100`

Returns recent backup log lines.

**Query Parameters**:
- `lines` (int, optional): Number of log lines to return (1-1000, default: 100)

**Response** (200 OK):
```json
{
  "logs": [
    "[2025-12-15 16:31:38] [INFO] Starting backup process...",
    "[2025-12-15 16:31:38] [INFO] Creating PostgreSQL backup...",
    "[2025-12-15 16:31:38] [INFO] ✓ Backup created: sentinel_backup_20251215_163138.sql.gz (236K)"
  ],
  "total_lines": 150
}
```

**Error Responses**:
- `422`: Invalid query parameters
- `500`: Failed to read log file

---

### 5. Get Backup Configuration

**GET** `/config`

Returns current backup system configuration.

**Response** (200 OK):
```json
{
  "backup_dir": "/var/backups/sentinel/postgres",
  "retention_days": 7,
  "s3_enabled": false,
  "minio_enabled": false,
  "encryption_enabled": false,
  "webhook_enabled": false
}
```

---

### 6. Health Check

**GET** `/health`

Simple health check endpoint for monitoring.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "backup-api"
}
```

---

## Data Models

### BackupFile

```typescript
{
  filename: string;           // Backup filename
  size_bytes: number;         // File size in bytes
  size_mb: number;            // File size in MB
  created_at: string;         // ISO timestamp
  age_hours: number;          // Age in hours
  has_checksum: boolean;      // SHA256 checksum exists
  is_encrypted: boolean;      // Encrypted with AES-256
}
```

### BackupMetrics

```typescript
{
  total_backups: number;              // Total backup count
  total_size_mb: number;              // Total size in MB
  oldest_backup_age_hours: number;    // Oldest backup age
  newest_backup_age_hours: number;    // Newest backup age
  average_size_mb: number;            // Average backup size
  success_rate_24h: number;           // Success rate (0-100)
}
```

---

## Usage Examples

### Python

```python
import requests

# Get status
response = requests.get("http://localhost:8000/api/v1/backup/status")
status = response.json()
print(f"Health: {status['health']}")
print(f"Total backups: {status['metrics']['total_backups']}")

# Trigger backup
response = requests.post("http://localhost:8000/api/v1/backup/trigger")
result = response.json()
print(f"Backup {result['status']}: {result['message']}")

# Get logs
response = requests.get("http://localhost:8000/api/v1/backup/logs?lines=50")
logs = response.json()
for log in logs['logs'][-10:]:
    print(log)
```

### JavaScript/TypeScript

```typescript
// Get status
const response = await fetch('/api/v1/backup/status');
const status = await response.json();
console.log(`Health: ${status.health}`);

// Trigger backup
const triggerResponse = await fetch('/api/v1/backup/trigger', {
  method: 'POST'
});
const result = await triggerResponse.json();
console.log(`Backup ${result.status}`);

// Get history with pagination
const historyResponse = await fetch('/api/v1/backup/history?limit=10&offset=0');
const backups = await historyResponse.json();
console.log(`Found ${backups.length} backups`);
```

### cURL

```bash
# Get status
curl http://localhost:8000/api/v1/backup/status

# Trigger backup
curl -X POST http://localhost:8000/api/v1/backup/trigger

# Get logs
curl "http://localhost:8000/api/v1/backup/logs?lines=50"

# Get configuration
curl http://localhost:8000/api/v1/backup/config
```

---

## Performance

- **Status endpoint**: <100ms (p95) with caching
- **History endpoint**: <200ms for 50 backups
- **Trigger endpoint**: 1-30 seconds (depends on DB size)
- **Logs endpoint**: <50ms for 100 lines

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200`: Success
- `404`: Resource not found
- `408`: Request timeout
- `422`: Validation error
- `500`: Internal server error

Error response format:
```json
{
  "detail": "Error message description"
}
```

---

## Rate Limiting

**TODO**: Implement rate limiting before production:
- Status: 60 requests/minute
- Trigger: 5 requests/minute
- Logs: 30 requests/minute

---

## Security Considerations

1. **Authentication**: Add JWT authentication
2. **Authorization**: Restrict trigger endpoint to admins
3. **Input Validation**: All inputs validated with Pydantic
4. **Log Sanitization**: Sensitive data filtered from logs
5. **CORS**: Configure allowed origins

---

## Testing

Run unit tests:
```bash
pytest backend/tests/test_backup_api.py -v
```

Run with coverage:
```bash
pytest backend/tests/test_backup_api.py --cov=app.routers.backup --cov-report=html
```

---

## Monitoring

### Prometheus Metrics

The API exposes metrics at `/metrics`:

```
# Backup API metrics
http_requests_total{endpoint="/api/v1/backup/status"}
http_request_duration_seconds{endpoint="/api/v1/backup/status"}
```

### Health Checks

Use `/api/v1/backup/health` for:
- Kubernetes liveness probes
- Load balancer health checks
- Monitoring systems

---

## Changelog

### v1.0.0 (2025-12-15)
- Initial release
- 6 endpoints implemented
- Caching for performance
- Comprehensive error handling
- Unit tests (>80% coverage)

---

## Support

For issues or questions:
- **Documentation**: This file
- **Tests**: `backend/tests/test_backup_api.py`
- **Source**: `backend/app/routers/backup.py`
