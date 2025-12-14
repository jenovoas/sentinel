from celery import Celery
from app.config import get_settings
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
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Celery Beat Schedule
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "collect-metrics": {
        "task": "app.tasks.monitoring.collect_metrics",
        "schedule": 15,  # Every 15 seconds (align with dashboard refresh)
    },
    "cleanup-old-metrics": {
        "task": "app.tasks.monitoring.cleanup_old_data",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "cleanup-old-audit-logs": {
        "task": "app.tasks.cleanup.cleanup_old_audit_logs",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    "health-check": {
        "task": "app.tasks.health.health_check",
        "schedule": 60,  # Every 60 seconds
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
