import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.redis_client import get_redis_master, get_redis_slave, close_redis
import app.redis_client

@pytest.mark.asyncio
async def test_redis_cleanup():
    # Reset global state
    app.redis_client._master = None
    app.redis_client._slave = None

    # Mock redis.from_url to return a mock Redis client
    mock_redis = AsyncMock()
    mock_redis.aclose = AsyncMock()

    with patch("redis.asyncio.from_url", return_value=mock_redis):
        with patch.dict("os.environ", {"REDIS_MODE": "standalone"}):
            app.redis_client.REDIS_MODE = "standalone"

            # Get connections
            master = await get_redis_master()
            slave = await get_redis_slave()

            assert master is mock_redis
            assert slave is mock_redis
            assert app.redis_client._master is mock_redis
            assert app.redis_client._slave is mock_redis

            # Close connections
            await close_redis()

            # Verify aclose was called
            mock_redis.aclose.assert_called_once()

            # Verify state was reset
            assert app.redis_client._master is None
            assert app.redis_client._slave is None

@pytest.mark.asyncio
async def test_redis_cleanup_sentinel():
    # Reset global state
    app.redis_client._master = None
    app.redis_client._slave = None

    mock_master = AsyncMock()
    mock_master.aclose = AsyncMock()

    mock_slave = AsyncMock()
    mock_slave.aclose = AsyncMock()

    mock_sentinel = MagicMock()
    mock_sentinel.master_for.return_value = mock_master
    mock_sentinel.slave_for.return_value = mock_slave

    with patch("app.redis_client.get_sentinel", return_value=mock_sentinel):
        with patch.dict("os.environ", {"REDIS_MODE": "sentinel"}):
            app.redis_client.REDIS_MODE = "sentinel"

            # Get connections
            master = await get_redis_master()
            slave = await get_redis_slave()

            assert master is mock_master
            assert slave is mock_slave

            # Close connections
            await close_redis()

            # Verify aclose was called on both
            mock_master.aclose.assert_called_once()
            mock_slave.aclose.assert_called_once()

            # Verify state was reset
            assert app.redis_client._master is None
            assert app.redis_client._slave is None
