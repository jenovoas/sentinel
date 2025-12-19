"""
PostgreSQL Session con Buffers Dinámicos
Integra adaptive_buffers en conexiones PostgreSQL
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator
import logging

from app.core.adaptive_buffers import (
    get_db_buffer_config,
    report_metrics,
    DataFlowType
)

logger = logging.getLogger(__name__)


class DynamicPostgreSQLSession:
    """
    PostgreSQL con buffers dinámicos adaptativos
    
    MEJORA: Pool y buffers se ajustan según carga
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session_maker = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inicializa engine con configuración dinámica"""
        config = get_db_buffer_config()
        
        # Crear engine con pool dinámico
        self.engine = create_async_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=config.pool_min_size,
            max_overflow=config.pool_max_size - config.pool_min_size,
            pool_timeout=config.connection_timeout,
            pool_recycle=3600,  # Reciclar conexiones cada hora
            echo=False,
            # Buffers dinámicos
            connect_args={
                "server_settings": {
                    "jit": "off",  # Desactivar JIT para latencia predecible
                },
                "command_timeout": config.read_timeout,
            }
        )
        
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info(
            f"PostgreSQL initialized with dynamic buffers: "
            f"pool={config.pool_min_size}-{config.pool_max_size}, "
            f"timeout={config.read_timeout}s"
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Obtiene sesión con monitoreo de métricas
        
        Reporta latencia para ajuste dinámico de buffers
        """
        import time
        start = time.time()
        
        async with self.session_maker() as session:
            try:
                yield session
                
                # Reportar métricas para ajuste dinámico
                latency_ms = (time.time() - start) * 1000
                report_metrics(
                    DataFlowType.DATABASE_QUERY,
                    latency_ms,
                    throughput=1.0  # 1 query
                )
                
            except Exception as e:
                logger.error(f"Database session error: {e}")
                raise
    
    async def close(self):
        """Cierra engine"""
        if self.engine:
            await self.engine.dispose()
            logger.info("PostgreSQL engine closed")


# Global instance (configurar con tu DATABASE_URL)
# db_session = DynamicPostgreSQLSession("postgresql+asyncpg://user:pass@localhost/sentinel_db")
