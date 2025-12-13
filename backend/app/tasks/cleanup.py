from app.celery_app import celery_app
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from app.database import get_db_context

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.cleanup.cleanup_old_audit_logs")
def cleanup_old_audit_logs(days: int = 90):
    """Remove audit logs older than specified days"""
    try:
        with get_db_context() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            db.execute(
                text("DELETE FROM audit_logs WHERE created_at < :cutoff_date"),
                {"cutoff_date": cutoff_date}
            )
            db.commit()
            logger.info(f"Cleaned up audit logs older than {days} days")
    except Exception as e:
        logger.error(f"Error cleaning up audit logs: {e}")
        raise


@celery_app.task(name="app.tasks.cleanup.send_email")
def send_email(to: str, subject: str, body: str):
    """Send email task (placeholder)"""
    try:
        logger.info(f"Would send email to {to}: {subject}")
        # In production, integrate with actual email service
        return {"status": "sent", "to": to}
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise
