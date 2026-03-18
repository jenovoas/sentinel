from celery import Celery
from app.config import get_settings
from app.quantum_scheduler import T_BIO, T_CYCLE
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "sentinel",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
# worker_prefetch_multiplier=1: no acumular tareas en el worker — el quantum
# scheduler decide cuándo ejecutar, no el prefetch del broker.
# worker_concurrency=2: alineado a los 2 vCPUs disponibles en sentinel.
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    worker_prefetch_multiplier=1,   # quantum-aware: no acumular
    worker_max_tasks_per_child=1000,
    worker_concurrency=2,           # alineado a vCPUs sentinel
)

# Celery Beat Schedule — alineado a ciclos S60
# T_BIO = 17s (pulso humano) — intervalo base de métricas
# T_CYCLE = 68s (4 × T_BIO) — ciclo completo para health-check
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "collect-metrics": {
        "task": "app.tasks.monitoring.collect_metrics",
        "schedule": T_BIO,           # 17s — alineado al pulso humano (era 15s)
    },
    "cleanup-old-metrics": {
        "task": "app.tasks.monitoring.cleanup_old_data",
        "schedule": crontab(hour=0, minute=0),
    },
    "cleanup-old-audit-logs": {
        "task": "app.tasks.cleanup.cleanup_old_audit_logs",
        "schedule": crontab(hour=2, minute=0),
    },
    "health-check": {
        "task": "app.tasks.health.health_check",
        "schedule": T_CYCLE,         # 68s — ciclo completo S60 (era 60s)
    },
}


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    logger.info(f"Request: {self.request!r}")
    return "Debug task executed"


# Auto-discover tasks from all app.tasks modules
celery_app.autodiscover_tasks(["app.tasks"])
logger.info("✅ Celery tasks auto-discovered")
