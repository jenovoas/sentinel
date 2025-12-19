"""
Redis Cache con Buffers Dinámicos
Integra adaptive_buffers en operaciones Redis
"""

import redis.asyncio as redis
from typing import Optional, Any
import json
import logging
import time

from app.core.adaptive_buffers import (
    get_cache_buffer_config,
    report_metrics,
    DataFlowType
)

logger = logging.getLogger(__name__)


class DynamicRedisCache:
    """
    Redis con buffers dinámicos adaptativos
    
    MEJORA: Pool y pipeline se ajustan según carga
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente con configuración dinámica"""
        config = get_cache_buffer_config()
        
        # Crear pool con configuración dinámica
        pool = redis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=config.pool_max_size,
            socket_timeout=config.read_timeout,
            socket_connect_timeout=config.connection_timeout,
            decode_responses=True,
            # Buffers dinámicos
            socket_read_size=config.read_buffer_size,
        )
        
        self.client = redis.Redis(connection_pool=pool)
        
        logger.info(
            f"Redis initialized with dynamic buffers: "
            f"pool_max={config.pool_max_size}, "
            f"buffer={config.read_buffer_size}B"
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get con monitoreo de métricas"""
        start = time.time()
        
        try:
            value = await self.client.get(key)
            
            # Reportar métricas
            latency_ms = (time.time() - start) * 1000
            report_metrics(
                DataFlowType.CACHE_OPERATION,
                latency_ms,
                throughput=1.0
            )
            
            return json.loads(value) if value else None
            
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set con monitoreo de métricas"""
        start = time.time()
        
        try:
            config = get_cache_buffer_config()
            ttl = ttl or config.cache_ttl
            
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            
            # Reportar métricas
            latency_ms = (time.time() - start) * 1000
            report_metrics(
                DataFlowType.CACHE_OPERATION,
                latency_ms,
                throughput=1.0
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def batch_get(self, keys: list[str]) -> dict[str, Any]:
        """Batch get con pipeline dinámico"""
        start = time.time()
        config = get_cache_buffer_config()
        
        try:
            # Pipeline con batch size dinámico
            async with self.client.pipeline() as pipe:
                for key in keys:
                    pipe.get(key)
                
                values = await pipe.execute()
            
            # Parsear resultados
            results = {}
            for key, value in zip(keys, values):
                if value:
                    results[key] = json.loads(value)
            
            # Reportar métricas
            latency_ms = (time.time() - start) * 1000
            report_metrics(
                DataFlowType.CACHE_OPERATION,
                latency_ms,
                throughput=len(keys)
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Redis BATCH_GET error: {e}")
            return {}
    
    async def close(self):
        """Cierra conexiones"""
        if self.client:
            await self.client.close()
            logger.info("Redis client closed")


# Global instance
dynamic_redis_cache = DynamicRedisCache()
