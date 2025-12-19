"""
Sentinel Global HA - Buffers Dinámicos Adaptativos
Aplica buffers dinámicos a TODA la arquitectura HA:
- PostgreSQL (queries)
- Redis (cache)
- Network (packets)
- LLM (inference)

INNOVACIÓN: Buffers se ajustan automáticamente según:
- Tipo de flujo de datos
- Carga del sistema
- Latencia observada
"""

import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataFlowType(Enum):
    """Tipos de flujo de datos en la arquitectura"""
    LLM_INFERENCE = "llm"           # Inferencia LLM
    DATABASE_QUERY = "db"           # Queries PostgreSQL
    CACHE_OPERATION = "cache"      # Operaciones Redis
    NETWORK_PACKET = "network"     # Paquetes de red
    TELEMETRY = "telemetry"        # Telemetría/logs


@dataclass
class DynamicBufferConfig:
    """
    Configuración dinámica de buffers según flujo
    
    OPTIMIZACIÓN CLAVE: Cada tipo de flujo tiene buffers optimizados
    """
    # Tamaños de buffer
    read_buffer_size: int = 8192      # Buffer lectura (bytes)
    write_buffer_size: int = 8192     # Buffer escritura (bytes)
    batch_size: int = 100             # Tamaño de batch
    prefetch_size: int = 10           # Prefetch count
    
    # Timeouts
    connection_timeout: float = 5.0   # Timeout conexión (s)
    read_timeout: float = 30.0        # Timeout lectura (s)
    
    # Pool sizes
    pool_min_size: int = 5            # Conexiones mínimas
    pool_max_size: int = 20           # Conexiones máximas
    
    # Cache
    cache_ttl: int = 300              # TTL cache (s)
    cache_max_entries: int = 1000     # Máx entradas cache


class AdaptiveBufferManager:
    """
    Gestor de buffers adaptativos para toda la arquitectura HA
    
    RESPONSABILIDAD:
    - Ajustar buffers según tipo de flujo
    - Monitorear latencias y ajustar dinámicamente
    - Optimizar uso de memoria
    """
    
    def __init__(self):
        self.configs: Dict[DataFlowType, DynamicBufferConfig] = {}
        self._initialize_configs()
        
        # Métricas para ajuste dinámico
        self.latencies: Dict[DataFlowType, list] = {
            flow: [] for flow in DataFlowType
        }
        self.throughputs: Dict[DataFlowType, list] = {
            flow: [] for flow in DataFlowType
        }
    
    def _initialize_configs(self):
        """Inicializa configuraciones optimizadas por tipo de flujo"""
        
        # LLM Inference: Buffers grandes, timeouts largos
        self.configs[DataFlowType.LLM_INFERENCE] = DynamicBufferConfig(
            read_buffer_size=16384,      # 16KB (respuestas largas)
            write_buffer_size=4096,      # 4KB (prompts cortos)
            batch_size=10,               # Batch pequeño (latencia)
            prefetch_size=2,             # Prefetch mínimo
            connection_timeout=10.0,     # Timeout largo (modelo carga)
            read_timeout=60.0,           # Timeout muy largo (generación)
            pool_min_size=2,             # Pool pequeño (GPU limitada)
            pool_max_size=5,
            cache_ttl=600,               # Cache largo (respuestas estables)
            cache_max_entries=500
        )
        
        # Database Query: Buffers medianos, pool grande
        self.configs[DataFlowType.DATABASE_QUERY] = DynamicBufferConfig(
            read_buffer_size=8192,       # 8KB (queries típicos)
            write_buffer_size=4096,      # 4KB (inserts pequeños)
            batch_size=100,              # Batch grande (throughput)
            prefetch_size=20,            # Prefetch alto (queries frecuentes)
            connection_timeout=3.0,      # Timeout corto
            read_timeout=10.0,           # Timeout medio
            pool_min_size=10,            # Pool grande (muchas conexiones)
            pool_max_size=50,
            cache_ttl=300,               # Cache medio
            cache_max_entries=2000
        )
        
        # Cache (Redis): Buffers pequeños, muy rápido
        self.configs[DataFlowType.CACHE_OPERATION] = DynamicBufferConfig(
            read_buffer_size=4096,       # 4KB (valores pequeños)
            write_buffer_size=4096,      # 4KB (valores pequeños)
            batch_size=500,              # Batch muy grande (rápido)
            prefetch_size=50,            # Prefetch muy alto
            connection_timeout=1.0,      # Timeout muy corto
            read_timeout=2.0,            # Timeout muy corto
            pool_min_size=20,            # Pool muy grande (muchas ops)
            pool_max_size=100,
            cache_ttl=60,                # Cache corto (datos volátiles)
            cache_max_entries=10000
        )
        
        # Network Packets: Buffers optimizados para MTU
        self.configs[DataFlowType.NETWORK_PACKET] = DynamicBufferConfig(
            read_buffer_size=65536,      # 64KB (MTU jumbo frames)
            write_buffer_size=65536,     # 64KB
            batch_size=1000,             # Batch muy grande (paquetes)
            prefetch_size=100,           # Prefetch muy alto
            connection_timeout=0.5,      # Timeout muy corto
            read_timeout=1.0,            # Timeout muy corto
            pool_min_size=50,            # Pool muy grande (muchas conexiones)
            pool_max_size=200,
            cache_ttl=10,                # Cache muy corto
            cache_max_entries=5000
        )
        
        # Telemetry: Buffers grandes, batch alto
        self.configs[DataFlowType.TELEMETRY] = DynamicBufferConfig(
            read_buffer_size=32768,      # 32KB (logs largos)
            write_buffer_size=16384,     # 16KB (logs batch)
            batch_size=1000,             # Batch muy grande (throughput)
            prefetch_size=0,             # Sin prefetch (streaming)
            connection_timeout=2.0,      # Timeout corto
            read_timeout=5.0,            # Timeout corto
            pool_min_size=5,             # Pool pequeño
            pool_max_size=20,
            cache_ttl=0,                 # Sin cache (datos únicos)
            cache_max_entries=0
        )
    
    def get_config(self, flow_type: DataFlowType) -> DynamicBufferConfig:
        """Obtiene configuración optimizada para tipo de flujo"""
        return self.configs[flow_type]
    
    def adjust_for_load(
        self,
        flow_type: DataFlowType,
        current_latency_ms: float,
        current_throughput: float
    ):
        """
        Ajusta buffers dinámicamente según carga observada
        
        ALGORITMO:
        - Alta latencia → Aumentar buffers (más batch)
        - Baja latencia → Reducir buffers (menos overhead)
        - Alto throughput → Aumentar pool
        - Bajo throughput → Reducir pool
        """
        config = self.configs[flow_type]
        
        # Guardar métricas
        self.latencies[flow_type].append(current_latency_ms)
        self.throughputs[flow_type].append(current_throughput)
        
        # Mantener solo últimas 100 muestras
        if len(self.latencies[flow_type]) > 100:
            self.latencies[flow_type].pop(0)
            self.throughputs[flow_type].pop(0)
        
        # Calcular promedios
        avg_latency = sum(self.latencies[flow_type]) / len(self.latencies[flow_type])
        avg_throughput = sum(self.throughputs[flow_type]) / len(self.throughputs[flow_type])
        
        # AJUSTE DINÁMICO
        
        # 1. Latencia alta → Aumentar buffers (más batch reduce overhead)
        if avg_latency > 1000:  # >1s
            config.batch_size = min(config.batch_size * 2, 2000)
            config.read_buffer_size = min(config.read_buffer_size * 2, 131072)  # Max 128KB
            logger.info(
                f"[{flow_type.value}] Alta latencia ({avg_latency:.0f}ms), "
                f"aumentando buffers: batch={config.batch_size}, "
                f"read_buf={config.read_buffer_size}"
            )
        
        # 2. Latencia baja → Reducir buffers (menos memoria)
        elif avg_latency < 100:  # <100ms
            config.batch_size = max(config.batch_size // 2, 10)
            config.read_buffer_size = max(config.read_buffer_size // 2, 4096)  # Min 4KB
            logger.info(
                f"[{flow_type.value}] Baja latencia ({avg_latency:.0f}ms), "
                f"reduciendo buffers: batch={config.batch_size}, "
                f"read_buf={config.read_buffer_size}"
            )
        
        # 3. Alto throughput → Aumentar pool
        if avg_throughput > 1000:  # >1000 ops/s
            config.pool_max_size = min(config.pool_max_size + 10, 500)
            logger.info(
                f"[{flow_type.value}] Alto throughput ({avg_throughput:.0f} ops/s), "
                f"aumentando pool: max={config.pool_max_size}"
            )
        
        # 4. Bajo throughput → Reducir pool (ahorrar recursos)
        elif avg_throughput < 100:  # <100 ops/s
            config.pool_max_size = max(config.pool_max_size - 5, config.pool_min_size)
            logger.info(
                f"[{flow_type.value}] Bajo throughput ({avg_throughput:.0f} ops/s), "
                f"reduciendo pool: max={config.pool_max_size}"
            )
    
    def get_buffer_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de buffers para monitoreo"""
        stats = {}
        
        for flow_type in DataFlowType:
            config = self.configs[flow_type]
            latencies = self.latencies[flow_type]
            throughputs = self.throughputs[flow_type]
            
            stats[flow_type.value] = {
                "buffer_config": {
                    "read_buffer_kb": config.read_buffer_size / 1024,
                    "write_buffer_kb": config.write_buffer_size / 1024,
                    "batch_size": config.batch_size,
                    "pool_max": config.pool_max_size
                },
                "metrics": {
                    "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
                    "avg_throughput": sum(throughputs) / len(throughputs) if throughputs else 0,
                    "samples": len(latencies)
                }
            }
        
        return stats


# Global instance
adaptive_buffer_manager = AdaptiveBufferManager()


# Helper functions para cada componente

def get_llm_buffer_config() -> DynamicBufferConfig:
    """Configuración de buffers para LLM"""
    return adaptive_buffer_manager.get_config(DataFlowType.LLM_INFERENCE)


def get_db_buffer_config() -> DynamicBufferConfig:
    """Configuración de buffers para PostgreSQL"""
    return adaptive_buffer_manager.get_config(DataFlowType.DATABASE_QUERY)


def get_cache_buffer_config() -> DynamicBufferConfig:
    """Configuración de buffers para Redis"""
    return adaptive_buffer_manager.get_config(DataFlowType.CACHE_OPERATION)


def get_network_buffer_config() -> DynamicBufferConfig:
    """Configuración de buffers para Network"""
    return adaptive_buffer_manager.get_config(DataFlowType.NETWORK_PACKET)


def get_telemetry_buffer_config() -> DynamicBufferConfig:
    """Configuración de buffers para Telemetry"""
    return adaptive_buffer_manager.get_config(DataFlowType.TELEMETRY)


def report_metrics(
    flow_type: DataFlowType,
    latency_ms: float,
    throughput: float
):
    """Reporta métricas para ajuste dinámico de buffers"""
    adaptive_buffer_manager.adjust_for_load(flow_type, latency_ms, throughput)
