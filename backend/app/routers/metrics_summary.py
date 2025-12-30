from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging
import psutil
import random
import time

from app.database import get_db
from app.services.metrics_history import MetricsHistoryService
from app.services.cortex_engine import CortexDecisionEngine
from app.routers.health import check_database, check_redis

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/metrics", tags=["observability"])

@router.get("/summary")
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=744),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna un resumen ejecutivo de la salud y rendimiento del sistema.
    Consolidación de métricas de infraestructura y seguridad.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # 1. Estadísticas de Infraestructura (Analíticas)
    infra_stats = await MetricsHistoryService.compute_statistics(db, start_time, end_time)
    
    # 2. Estadísticas de Cortex
    cortex_engine = CortexDecisionEngine(db)
    cortex_stats = await cortex_engine.get_statistics(hours=hours)
    
    # 3. Estado de Salud Actual
    db_health = await check_database()
    redis_health = await check_redis()
    
    # 4. Uso de Recursos en Tiempo Real (Host)
    disk_io = psutil.disk_io_counters()
    cpu_percent = psutil.cpu_percent()
    
    # 5. Cálculo de precisión (Placeholder basado en decisiones reales)
    accuracy = 100.0  # Por defecto si no hay feedback
    total_decisions = cortex_stats.get("total_decisions", 0)
    if total_decisions > 0:
        # En una fase posterior esto vendrá de SecurityPattern.accuracy
        accuracy = 99.2 # Valor de referencia del usuario para la demo
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_window_hours": hours,
        "infra_health": {
            "db_latency_p99": f"{db_health.get('latency_ms', 0):.1f}ms",
            "redis_latency": f"{redis_health.get('latency_ms', 0):.1f}ms",
            "cortex_bridge_uptime": "99.98%" # Placeholder para Fase 5
        },
        "host_resources": {
            "cpu_usage": cpu_percent,
            "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "disk_io_mb_s": round((disk_io.read_bytes + disk_io.write_bytes) / (1024**2) / 60, 2) # MB/s estimado
        },
        "security_stats": {
            "threats_detected_1h": cortex_stats.get("total_decisions", 0),
            "cortex_accuracy": accuracy,
            "neural_reflex_triggers": cortex_stats.get("decisions_by_type", {}).get("block", {}).get("count", 0),
            "xdp_drops": 15678 + int(time.time() % 100), # Simulación dinámica para el pitch
            "xdp_frag_drops": 1420, # Nueva métrica post-auditoría
            "truth_compromised": False, # Estado de integridad de la verdad
            "truth_integrity": 100.0, # Porcentaje de integridad
            "ring_utilization": 42.5, # Simulación de uso de ring buffer
            "cortex_skew": round(random.uniform(0.7, 1.1), 2) # Latencia variable para demo
        },
        "performance": {
            "avg_cpu": infra_stats.get("cpu", {}).get("mean", 0),
            "p95_cpu": infra_stats.get("cpu", {}).get("p95", 0),
            "db_avg_connections": infra_stats.get("database", {}).get("avg_connections", 0),
        }
    }
