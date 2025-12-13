from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.health.health_check")
def health_check():
    """Periodic health check task"""
    try:
        logger.debug("Health check executed")
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise
