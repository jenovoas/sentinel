"""
Unit Tests for Backup API Router

Tests all backup API endpoints for correct behavior, error handling,
and response validation.

Run with: pytest backend/tests/test_backup_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import tempfile
import time

from app.main import app

client = TestClient(app)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_backup_dir(tmp_path):
    """Create a temporary backup directory with test files"""
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    
    # Create test backup files
    for i in range(3):
        backup_file = backup_dir / f"sentinel_backup_20251215_16000{i}.sql.gz"
        backup_file.write_text("test backup data")
        
        # Create checksum file
        checksum_file = backup_dir / f"sentinel_backup_20251215_16000{i}.sql.gz.sha256"
        checksum_file.write_text("abc123def456")
    
    return str(backup_dir)


@pytest.fixture
def mock_log_file(tmp_path):
    """Create a temporary log file with test data"""
    log_file = tmp_path / "backup.log"
    log_content = """[2025-12-15 16:00:00] [INFO] Starting backup process...
[2025-12-15 16:00:15] [INFO] Backup created: sentinel_backup_20251215_160000.sql.gz (236K)
[2025-12-15 16:00:16] [INFO] ✓ Backup validation passed
[2025-12-15 16:00:17] [INFO] ✓ Backup process completed successfully
"""
    log_file.write_text(log_content)
    return str(log_file)


# ============================================================================
# TESTS: /api/v1/backup/status
# ============================================================================

def test_backup_status_endpoint_success(mock_backup_dir, mock_log_file):
    """Test backup status returns valid data"""
    with patch.dict(os.environ, {"BACKUP_DIR": mock_backup_dir, "LOG_FILE": mock_log_file}):
        response = client.get("/api/v1/backup/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "health" in data
        assert data["health"] in ["healthy", "warning", "critical"]
        
        assert "last_backup" in data
        assert "status" in data["last_backup"]
        
        assert "metrics" in data
        assert "total_backups" in data["metrics"]
        assert data["metrics"]["total_backups"] == 3
        
        assert "backups" in data
        assert len(data["backups"]) == 3
        
        assert "config" in data
        assert data["config"]["backup_dir"] == mock_backup_dir


def test_backup_status_endpoint_no_backups():
    """Test backup status with no backups"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.dict(os.environ, {"BACKUP_DIR": tmp_dir}):
            response = client.get("/api/v1/backup/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["metrics"]["total_backups"] == 0
            assert len(data["backups"]) == 0


def test_backup_status_caching():
    """Test that status is cached for performance"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with patch.dict(os.environ, {"BACKUP_DIR": tmp_dir}):
            # First request
            response1 = client.get("/api/v1/backup/status")
            assert response1.status_code == 200
            
            # Second request (should be cached)
            response2 = client.get("/api/v1/backup/status")
            assert response2.status_code == 200
            
            # Responses should be identical (from cache)
            assert response1.json() == response2.json()


# ============================================================================
# TESTS: /api/v1/backup/history
# ============================================================================

def test_backup_history_endpoint(mock_backup_dir):
    """Test backup history returns paginated results"""
    with patch.dict(os.environ, {"BACKUP_DIR": mock_backup_dir}):
        response = client.get("/api/v1/backup/history?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Validate backup file structure
        backup = data[0]
        assert "filename" in backup
        assert "size_bytes" in backup
        assert "size_mb" in backup
        assert "created_at" in backup
        assert "age_hours" in backup
        assert "has_checksum" in backup


def test_backup_history_pagination():
    """Test pagination works correctly"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create 10 test backups
        for i in range(10):
            backup_file = os.path.join(tmp_dir, f"sentinel_backup_2025121{i}_160000.sql.gz")
            with open(backup_file, 'w') as f:
                f.write("test")
        
        with patch.dict(os.environ, {"BACKUP_DIR": tmp_dir}):
            # Get first 5
            response1 = client.get("/api/v1/backup/history?limit=5&offset=0")
            assert response1.status_code == 200
            assert len(response1.json()) == 5
            
            # Get next 5
            response2 = client.get("/api/v1/backup/history?limit=5&offset=5")
            assert response2.status_code == 200
            assert len(response2.json()) == 5


def test_backup_history_invalid_params():
    """Test validation of query parameters"""
    # Limit too high
    response = client.get("/api/v1/backup/history?limit=1000")
    assert response.status_code == 422  # Validation error
    
    # Negative offset
    response = client.get("/api/v1/backup/history?offset=-1")
    assert response.status_code == 422


# ============================================================================
# TESTS: /api/v1/backup/trigger
# ============================================================================

@patch('subprocess.run')
def test_backup_trigger_success(mock_run):
    """Test successful backup trigger"""
    # Mock successful backup execution
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Backup completed successfully",
        stderr=""
    )
    
    response = client.post("/api/v1/backup/trigger")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "success"
    assert data["exit_code"] == 0
    assert "successfully" in data["message"].lower()


@patch('subprocess.run')
def test_backup_trigger_failure(mock_run):
    """Test failed backup trigger"""
    # Mock failed backup execution
    mock_run.return_value = MagicMock(
        returncode=1,
        stdout="",
        stderr="Backup failed: permission denied"
    )
    
    response = client.post("/api/v1/backup/trigger")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "failed"
    assert data["exit_code"] == 1


@patch('subprocess.run')
def test_backup_trigger_timeout(mock_run):
    """Test backup trigger timeout"""
    import subprocess
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="backup.sh", timeout=300)
    
    response = client.post("/api/v1/backup/trigger")
    
    assert response.status_code == 408  # Timeout
    assert "timeout" in response.json()["detail"].lower()


# ============================================================================
# TESTS: /api/v1/backup/logs
# ============================================================================

def test_backup_logs_endpoint(mock_log_file):
    """Test backup logs returns recent lines"""
    with patch.dict(os.environ, {"LOG_FILE": mock_log_file}):
        response = client.get("/api/v1/backup/logs?lines=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total_lines" in data
        assert isinstance(data["logs"], list)
        assert len(data["logs"]) > 0


def test_backup_logs_no_file():
    """Test logs endpoint when file doesn't exist"""
    with patch.dict(os.environ, {"LOG_FILE": "/nonexistent/file.log"}):
        response = client.get("/api/v1/backup/logs")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["logs"] == []
        assert data["total_lines"] == 0


def test_backup_logs_line_limit():
    """Test log line limit validation"""
    # Too many lines
    response = client.get("/api/v1/backup/logs?lines=10000")
    assert response.status_code == 422  # Validation error


# ============================================================================
# TESTS: /api/v1/backup/config
# ============================================================================

def test_backup_config_endpoint():
    """Test backup configuration endpoint"""
    with patch.dict(os.environ, {
        "BACKUP_DIR": "/custom/backup/dir",
        "BACKUP_RETENTION_DAYS": "14",
        "S3_ENABLED": "true",
        "ENCRYPT_ENABLED": "true"
    }):
        response = client.get("/api/v1/backup/config")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["backup_dir"] == "/custom/backup/dir"
        assert data["retention_days"] == 14
        assert data["s3_enabled"] is True
        assert data["encryption_enabled"] is True


def test_backup_config_defaults():
    """Test configuration defaults"""
    # Clear environment variables
    env_vars = ["BACKUP_DIR", "BACKUP_RETENTION_DAYS", "S3_ENABLED"]
    with patch.dict(os.environ, {k: "" for k in env_vars}, clear=True):
        response = client.get("/api/v1/backup/config")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use defaults
        assert data["retention_days"] == 7
        assert data["s3_enabled"] is False


# ============================================================================
# TESTS: /api/v1/backup/health
# ============================================================================

def test_backup_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/backup/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["service"] == "backup-api"


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_full_backup_workflow(mock_backup_dir, mock_log_file):
    """Test complete backup workflow"""
    with patch.dict(os.environ, {"BACKUP_DIR": mock_backup_dir, "LOG_FILE": mock_log_file}):
        # 1. Check initial status
        status_response = client.get("/api/v1/backup/status")
        assert status_response.status_code == 200
        initial_count = status_response.json()["metrics"]["total_backups"]
        
        # 2. Get configuration
        config_response = client.get("/api/v1/backup/config")
        assert config_response.status_code == 200
        
        # 3. Get history
        history_response = client.get("/api/v1/backup/history")
        assert history_response.status_code == 200
        
        # 4. Get logs
        logs_response = client.get("/api/v1/backup/logs")
        assert logs_response.status_code == 200
        
        # All endpoints should work
        assert all([
            status_response.status_code == 200,
            config_response.status_code == 200,
            history_response.status_code == 200,
            logs_response.status_code == 200
        ])


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_error_handling_invalid_backup_dir():
    """Test graceful handling of invalid backup directory"""
    with patch.dict(os.environ, {"BACKUP_DIR": "/invalid/path/that/does/not/exist"}):
        response = client.get("/api/v1/backup/status")
        
        # Should not crash, should return empty results
        assert response.status_code == 200
        data = response.json()
        assert data["metrics"]["total_backups"] == 0


def test_error_handling_corrupted_log():
    """Test handling of corrupted log file"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        # Write invalid data
        f.write("\x00\x01\x02\x03")
        log_file = f.name
    
    try:
        with patch.dict(os.environ, {"LOG_FILE": log_file}):
            response = client.get("/api/v1/backup/logs")
            
            # Should handle gracefully
            assert response.status_code in [200, 500]
    finally:
        os.unlink(log_file)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_status_endpoint_performance(mock_backup_dir):
    """Test status endpoint responds quickly"""
    with patch.dict(os.environ, {"BACKUP_DIR": mock_backup_dir}):
        start_time = time.time()
        response = client.get("/api/v1/backup/status")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond in less than 1 second
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response took {response_time}s (should be <1s)"
