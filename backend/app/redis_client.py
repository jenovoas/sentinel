"""
Redis Sentinel Client for High Availability

Provides automatic failover support for Redis connections.
Backend will automatically reconnect to new master when failover occurs.

Usage:
    from app.redis_client import get_redis_master, get_redis_slave
    
    # For writes
    master = await get_redis_master()
    await master.set("key", "value")
    
    # For reads (load balanced across replicas)
    slave = await get_redis_slave()
    value = await slave.get("key")
"""

import logging
import os
from typing import Optional
import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel

logger = logging.getLogger(__name__)

from app.config import get_settings
settings = get_settings()

# REDIS_MODE: 'standalone' or 'sentinel'
REDIS_MODE = os.getenv("REDIS_MODE", "standalone").lower()

# Global instances
_sentinel: Optional[Sentinel] = None
_redis_standalone: Optional[redis.Redis] = None


def get_sentinel() -> Sentinel:
    """
    Get or create Redis Sentinel instance
    
    Sentinel monitors Redis master and automatically handles failover.
    
    Returns:
        Sentinel: Redis Sentinel instance
    """
    global _sentinel
    
    if _sentinel is None:
        # List of Sentinel instances
        # In production, these should be from environment variables
        sentinels = [
            ('redis-sentinel-1', 26379),
            ('redis-sentinel-2', 26379),
            ('redis-sentinel-3', 26379),
        ]
        
        _sentinel = Sentinel(
            sentinels,
            socket_timeout=0.5,
            socket_connect_timeout=0.5,
            decode_responses=True,  # Automatically decode bytes to strings
        )
        
        logger.info(f"✅ Redis Sentinel initialized with {len(sentinels)} sentinels")
    
    return _sentinel


async def get_redis_master() -> redis.Redis:
    """Get Redis connection for writes (master or standalone)"""
    if REDIS_MODE == "sentinel":
        sentinel = get_sentinel()
        return sentinel.master_for(
            'mymaster',
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
            decode_responses=True,
        )
    else:
        # Standalone mode
        return redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
        )


async def get_redis_slave() -> redis.Redis:
    """Get Redis connection for reads (slave or standalone)"""
    if REDIS_MODE == "sentinel":
        sentinel = get_sentinel()
        return sentinel.slave_for(
            'mymaster',
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
            decode_responses=True,
        )
    else:
        # In standalone, slave is the same as master
        return await get_redis_master()


async def check_redis_health() -> dict:
    """
    Check Redis cluster health
    
    Returns:
        dict: Health status including master info and replica count
    """
    if REDIS_MODE != "sentinel":
        try:
            master = await get_redis_master()
            await master.ping()
            return {
                "status": "healthy",
                "mode": "standalone"
            }
        except Exception as e:
            logger.error(f"Redis standalone health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    try:
        sentinel = get_sentinel()
        
        # Get master info
        master_info = await sentinel.discover_master('mymaster')
        
        # Get replicas info
        replicas_info = await sentinel.discover_slaves('mymaster')
        
        # Check if we can connect to master
        master = await get_redis_master()
        await master.ping()
        
        return {
            "status": "healthy",
            "master": {
                "host": master_info[0],
                "port": master_info[1],
            },
            "replicas_count": len(replicas_info),
            "replicas": [
                {"host": r[0], "port": r[1]}
                for r in replicas_info
            ]
        }
        
    except Exception as e:
        logger.error(f"Redis sentinel health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def test_failover():
    """
    Test Redis failover mechanism
    
    This simulates a master failure and verifies automatic failover.
    
    WARNING: This will cause a brief service interruption!
    Only use in testing environments.
    """
    logger.warning("⚠️ Testing Redis failover - this will cause brief interruption!")
    
    try:
        # 1. Get current master
        sentinel = get_sentinel()
        master_info = await sentinel.discover_master('mymaster')
        logger.info(f"Current master: {master_info[0]}:{master_info[1]}")
        
        # 2. Force failover
        await sentinel.sentinel_failover('mymaster')
        logger.info("Failover triggered...")
        
        # 3. Wait for new master
        import asyncio
        await asyncio.sleep(5)
        
        # 4. Get new master
        new_master_info = await sentinel.discover_master('mymaster')
        logger.info(f"New master: {new_master_info[0]}:{new_master_info[1]}")
        
        # 5. Verify we can still write
        master = await get_redis_master()
        await master.set("failover_test", "success")
        value = await master.get("failover_test")
        
        if value == "success":
            logger.info("✅ Failover test successful!")
            return True
        else:
            logger.error("❌ Failover test failed - could not write to new master")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failover test failed: {e}")
        return False


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Test connection
        master = await get_redis_master()
        await master.set("test_key", "test_value")
        
        slave = await get_redis_slave()
        value = await slave.get("test_key")
        
        print(f"Value from slave: {value}")
        
        # Check health
        health = await check_redis_health()
        print(f"Redis health: {health}")
    
    asyncio.run(main())
