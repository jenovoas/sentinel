"""
Redis Client for Standalone Mode

Simple Redis client for single-instance deployments.
For HA deployments, use redis_client_ha.py with Sentinel.

Usage:
    from app.redis_client import get_redis_master, get_redis_slave
    
    # For writes
    master = await get_redis_master()
    await master.set("key", "value")
    
    # For reads (same as master in standalone mode)
    slave = await get_redis_slave()
    value = await slave.get("key")
"""

import logging
import os
from typing import Optional
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Global Redis instance
_redis_client: Optional[redis.Redis] = None


def get_redis_url() -> str:
    """
    Get Redis URL from environment
    
    Returns:
        str: Redis connection URL
    """
    return os.getenv("REDIS_URL", "redis://redis:6379/0")


async def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client instance
    
    Returns:
        redis.Redis: Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        redis_url = get_redis_url()
        _redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        logger.info(f"✅ Redis client initialized: {redis_url}")
    
    return _redis_client


async def get_redis_master() -> redis.Redis:
    """
    Get Redis connection for writes
    
    In standalone mode, this is the same as get_redis_client().
    Kept for API compatibility with Sentinel mode.
    
    Returns:
        redis.Redis: Redis client instance
    """
    return await get_redis_client()


async def get_redis_slave() -> redis.Redis:
    """
    Get Redis connection for reads
    
    In standalone mode, this is the same as get_redis_client().
    Kept for API compatibility with Sentinel mode.
    
    Returns:
        redis.Redis: Redis client instance
    """
    return await get_redis_client()


async def check_redis_health() -> dict:
    """
    Check Redis health
    
    Returns:
        dict: Health status
    """
    try:
        client = await get_redis_client()
        await client.ping()
        
        # Get server info
        info = await client.info("server")
        
        return {
            "status": "healthy",
            "mode": "standalone",
            "redis_version": info.get("redis_version", "unknown"),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Test connection
        client = await get_redis_client()
        await client.set("test_key", "test_value")
        value = await client.get("test_key")
        
        print(f"Value from Redis: {value}")
        
        # Check health
        health = await check_redis_health()
        print(f"Redis health: {health}")
    
    asyncio.run(main())

