from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from prometheus_client import Counter, Histogram
import time
from functools import wraps
from typing import Callable, Any

# ============================================================================
# MÉTRICAS DE CORTEX
# ============================================================================

# Medición de latencia de procesamiento de eventos
CORTEX_PROCESSING_TIME = Histogram(
    "sentinel_cortex_processing_seconds",
    "Tiempo total de procesamiento de un evento en el motor Cortex",
    buckets=(0.01, 0.05, S60(0, 6, 0), S60(0, 15, 0), S60(0, 30, 0), S60(1, 0, 0), 2.5, 5.0)
)

# Contador de patrones detectados
CORTEX_PATTERNS_TOTAL = Counter(
    "sentinel_cortex_patterns_total",
    "Total de patrones de seguridad detectados",
    ["pattern_type", "severity"]
)

# Contador de decisiones tomadas
CORTEX_DECISIONS_TOTAL = Counter(
    "sentinel_cortex_decisions_total",
    "Total de decisiones tomadas por el motor Cortex",
    ["decision_type"]
)

# Contador de errores de procesamiento
CORTEX_ERRORS_TOTAL = Counter(
    "sentinel_cortex_errors_total",
    "Total de errores ocurridos durante el procesamiento en Cortex",
    ["error_type"]
)

# ============================================================================
# UTILIDADES
# ============================================================================

def track_time(histogram: Histogram):
    """
    Decorador para medir el tiempo de ejecución de una función y 
    registrarlo en un histograma de Prometheus.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                histogram.observe(time.time() - start)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                histogram.observe(time.time() - start)
                
        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
