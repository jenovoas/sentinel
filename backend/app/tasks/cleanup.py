from app.celery_app import celery_app
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import text
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.cleanup.cleanup_old_audit_logs")
def cleanup_old_audit_logs(days: int = 90):
    """Remove audit logs older than specified days"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_cleanup():
            async with AsyncSessionLocal() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                await session.execute(
                    text("DELETE FROM audit_logs WHERE created_at < :cutoff_date"),
                    {"cutoff_date": cutoff_date}
                )
                await session.commit()
                return {"success": True}

        result = loop.run_until_complete(run_cleanup())
        loop.close()

        logger.info(f"✅ Cleaned up audit logs older than {days} days")
        return result
    except Exception as e:
        logger.error(f"❌ Error cleaning up audit logs: {e}", exc_info=True)
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
