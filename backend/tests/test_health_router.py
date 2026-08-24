import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.routers.health import check_redis, check_database

client = TestClient(app)


@pytest.mark.asyncio
async def test_check_redis_sentinel_success():
    """Test check_redis when Sentinel mode succeeds"""
    mock_master = AsyncMock()
    mock_master.ping = AsyncMock(return_value=True)
    mock_master.set = AsyncMock(return_value=True)
    mock_master.get = AsyncMock(return_value="ok")

    mock_cluster_info = {
        "status": "healthy",
        "mode": "sentinel",
        "master": "mymaster"
    }

    with patch("app.redis_client.get_redis_master", return_value=mock_master), \
         patch("app.redis_client.check_redis_health", return_value=mock_cluster_info):
        result = await check_redis()
        assert result["status"] == "healthy"
        assert result["mode"] == "sentinel"
        assert "latency_ms" in result
        assert result["cluster"] == mock_cluster_info


@pytest.mark.asyncio
async def test_check_redis_sentinel_exception_fallback_standalone_success():
    """Test check_redis falls back to standalone mode when Sentinel raises an exception"""
    mock_standalone_redis = AsyncMock()
    mock_standalone_redis.ping = AsyncMock(return_value=True)
    mock_standalone_redis.set = AsyncMock(return_value=True)
    mock_standalone_redis.get = AsyncMock(return_value="ok")
    mock_standalone_redis.close = AsyncMock()

    # get_redis_master raises Exception to trigger Sentinel fallback
    with patch("app.redis_client.get_redis_master", side_effect=Exception("Sentinel connection failed")), \
         patch("redis.asyncio.from_url", return_value=mock_standalone_redis):
        result = await check_redis()
        assert result["status"] == "healthy"
        assert result["mode"] == "standalone"
        assert "latency_ms" in result


@pytest.mark.asyncio
async def test_check_redis_sentinel_ping_exception_fallback_standalone():
    """Test check_redis falls back to standalone mode when Sentinel ping throws Exception"""
    mock_master = AsyncMock()
    mock_master.ping = AsyncMock(side_effect=Exception("Ping timeout on Sentinel master"))

    mock_standalone_redis = AsyncMock()
    mock_standalone_redis.ping = AsyncMock(return_value=True)
    mock_standalone_redis.set = AsyncMock(return_value=True)
    mock_standalone_redis.get = AsyncMock(return_value="ok")
    mock_standalone_redis.close = AsyncMock()

    with patch("app.redis_client.get_redis_master", return_value=mock_master), \
         patch("redis.asyncio.from_url", return_value=mock_standalone_redis):
        result = await check_redis()
        assert result["status"] == "healthy"
        assert result["mode"] == "standalone"


@pytest.mark.asyncio
async def test_check_redis_both_sentinel_and_standalone_fail():
    """Test check_redis outer exception handling when both Sentinel and standalone fail"""
    with patch("app.redis_client.get_redis_master", side_effect=Exception("Sentinel fail")), \
         patch("redis.asyncio.from_url", side_effect=Exception("Standalone connection refused")):
        result = await check_redis()
        assert result["status"] == "unhealthy"
        assert "Standalone connection refused" in result["error"]


@pytest.mark.asyncio
async def test_check_redis_sentinel_value_mismatch_fallback_standalone_success():
    """Test check_redis when set/get test fails in Sentinel mode, triggering fallback to standalone"""
    mock_master = AsyncMock()
    mock_master.ping = AsyncMock(return_value=True)
    mock_master.set = AsyncMock(return_value=True)
    mock_master.get = AsyncMock(return_value="corrupted_value")

    mock_standalone_redis = AsyncMock()
    mock_standalone_redis.ping = AsyncMock(return_value=True)
    mock_standalone_redis.set = AsyncMock(return_value=True)
    mock_standalone_redis.get = AsyncMock(return_value="ok")
    mock_standalone_redis.close = AsyncMock()

    with patch("app.redis_client.get_redis_master", return_value=mock_master), \
         patch("redis.asyncio.from_url", return_value=mock_standalone_redis):
        result = await check_redis()
        assert result["status"] == "healthy"
        assert result["mode"] == "standalone"


@pytest.mark.asyncio
async def test_check_redis_standalone_value_mismatch():
    """Test check_redis when set/get test fails in standalone mode"""
    mock_standalone_redis = AsyncMock()
    mock_standalone_redis.ping = AsyncMock(return_value=True)
    mock_standalone_redis.set = AsyncMock(return_value=True)
    mock_standalone_redis.get = AsyncMock(return_value="wrong_value")
    mock_standalone_redis.close = AsyncMock()

    with patch("app.redis_client.get_redis_master", side_effect=Exception("Sentinel not configured")), \
         patch("redis.asyncio.from_url", return_value=mock_standalone_redis):
        result = await check_redis()
        assert result["status"] == "unhealthy"
        assert "Redis set/get test failed" in result["error"]


def test_health_endpoint_healthy():
    """Test GET /api/v1/health when database and redis are healthy"""
    with patch("app.routers.health.check_database", AsyncMock(return_value={"status": "healthy"})), \
         patch("app.routers.health.check_redis", AsyncMock(return_value={"status": "healthy"})):
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["components"]["database"]["status"] == "healthy"
        assert data["components"]["redis"]["status"] == "healthy"


def test_health_endpoint_unhealthy():
    """Test GET /api/v1/health when redis check returns unhealthy"""
    with patch("app.routers.health.check_database", AsyncMock(return_value={"status": "healthy"})), \
         patch("app.routers.health.check_redis", AsyncMock(return_value={"status": "unhealthy", "error": "Connection error"})):
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "unhealthy"


def test_ready_endpoint_healthy():
    """Test GET /api/v1/ready endpoint when components are healthy and role allows serving"""
    with patch("app.routers.health.check_database", AsyncMock(return_value={"status": "healthy"})), \
         patch("app.routers.health.check_redis", AsyncMock(return_value={"status": "healthy"})), \
         patch("app.routers.health.app_role", "primary"):
        response = client.get("/api/v1/ready")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ready"] is True


def test_ready_endpoint_unhealthy_redis():
    """Test GET /api/v1/ready endpoint when redis component is unhealthy"""
    with patch("app.routers.health.check_database", AsyncMock(return_value={"status": "healthy"})), \
         patch("app.routers.health.check_redis", AsyncMock(return_value={"status": "unhealthy", "error": "down"})), \
         patch("app.routers.health.app_role", "primary"):
        response = client.get("/api/v1/ready")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["ready"] is False


def test_live_endpoint():
    """Test GET /api/v1/live endpoint"""
    response = client.get("/api/v1/live")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["alive"] is True
