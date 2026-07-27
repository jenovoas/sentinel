import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

from app.redis_client import get_redis_master, get_redis_slave, close_redis, REDIS_MODE
from app.shutdown import graceful_shutdown

@pytest.mark.asyncio
async def test_redis_client_caching_and_cleanup():
    """Test that Redis client instances are cached and properly closed on close_redis()"""
    # 1. Mock redis.from_url to return a mock Redis instance
    mock_redis_client = MagicMock()
    mock_redis_client.close = AsyncMock()

    with patch("redis.asyncio.from_url", return_value=mock_redis_client) as mock_from_url:
        # Get master
        master = await get_redis_master()
        assert master is mock_redis_client
        mock_from_url.assert_called_once()

        # Get master again (should return cached instance, not call from_url again)
        master_again = await get_redis_master()
        assert master_again is master
        assert mock_from_url.call_count == 1

        # Get slave (should return cached master in standalone mode)
        slave = await get_redis_slave()
        assert slave is master

        # Close redis
        await close_redis()

        # Verify close was called on the mock client
        mock_redis_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_graceful_shutdown_triggers_redis_cleanup():
    """Test that graceful_shutdown calls close_redis and other cleanups"""
    # Patch all the systems involved in graceful_shutdown so we don't actually sleep/exit
    with patch("asyncio.sleep", AsyncMock()), \
         patch("app.shutdown.close_db", AsyncMock()) as mock_close_db, \
         patch("app.shutdown.close_redis", AsyncMock()) as mock_close_redis, \
         patch("logging.shutdown") as mock_logging_shutdown, \
         patch("sys.exit") as mock_sys_exit:

         await graceful_shutdown()

         # Verify close_db was called
         mock_close_db.assert_called_once()
         # Verify close_redis was called
         mock_close_redis.assert_called_once()
         # Verify logging shutdown was called
         mock_logging_shutdown.assert_called_once()
         # Verify sys.exit(0) was called
         mock_sys_exit.assert_called_once_with(0)
