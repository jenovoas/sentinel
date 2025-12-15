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
from typing import Optional
import redis.asyncio as redis
from redis.asyncio.sentinel import Sentinel

logger = logging.getLogger(__name__)

# Global Sentinel instance
_sentinel: Optional[Sentinel] = None


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
    """
    Get Redis master connection for writes
    
    Automatically connects to current master.
    If master fails, Sentinel will promote a replica and this will
    automatically connect to the new master.
    
    Returns:
        redis.Redis: Connection to Redis master
    """
    sentinel = get_sentinel()
    
    # Get master connection
    # 'mymaster' is the name we configured in sentinel.conf
    master = sentinel.master_for(
        'mymaster',
        socket_timeout=1.0,
        socket_connect_timeout=1.0,
        decode_responses=True,
    )
    
    return master


async def get_redis_slave() -> redis.Redis:
    """
    Get Redis slave connection for reads
    
    Automatically load balances across available replicas.
    Use this for read-heavy operations to offload master.
    
    Returns:
        redis.Redis: Connection to Redis replica
    """
    sentinel = get_sentinel()
    
    # Get slave connection (load balanced)
    slave = sentinel.slave_for(
        'mymaster',
        socket_timeout=1.0,
        socket_connect_timeout=1.0,
        decode_responses=True,
    )
    
    return slave


async def check_redis_health() -> dict:
    """
    Check Redis cluster health
    
    Returns:
        dict: Health status including master info and replica count
    """
    try:
        sentinel = get_sentinel()
        
        # Get master info
        master_info = sentinel.discover_master('mymaster')
        
        # Get replicas info
        replicas_info = sentinel.discover_slaves('mymaster')
        
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
        logger.error(f"Redis health check failed: {e}")
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
        master_info = sentinel.discover_master('mymaster')
        logger.info(f"Current master: {master_info[0]}:{master_info[1]}")
        
        # 2. Force failover
        sentinel.sentinel_failover('mymaster')
        logger.info("Failover triggered...")
        
        # 3. Wait for new master
        import asyncio
        await asyncio.sleep(5)
        
        # 4. Get new master
        new_master_info = sentinel.discover_master('mymaster')
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
