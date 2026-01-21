"""
Monitoring Tasks - Phase 2
Async tasks for metrics collection, anomaly detection, and historical storage
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.services.metrics_history import MetricsHistoryService
from app.services.monitoring_orchestrator import MonitoringOrchestrator


logger = logging.getLogger("monitoring.tasks")


@celery_app.task(name="app.tasks.monitoring.collect_metrics")
def collect_metrics_task():
    """
    Periodic task: Collect metrics, detect anomalies, store history.
    Runs every 15 seconds (configurable in config).

    Returns:
        dict: Collection results with anomaly count
    """
    try:
        # Create async session in sync context using run_until_complete
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_collection():
            async with AsyncSessionLocal() as session:
                result = await MonitoringOrchestrator.collect_and_process_metrics(session)
                return result

        result = loop.run_until_complete(run_collection())
        loop.close()

        if result.get("success"):
            logger.info(
                f"✅ Metrics collected: {result.get('anomalies_detected', 0)} anomalies detected"
            )
        else:
            logger.error(f"❌ Metrics collection failed: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"❌ Task error in collect_metrics: {e}", exc_info=True)
        raise


@celery_app.task(name="app.tasks.monitoring.cleanup_old_data")
def cleanup_old_data_task():
    """
    Periodic task: Clean up old metric samples and resolved anomalies.
    Runs daily at midnight.

    Keeps last 90 days of metrics data.
    """
    try:
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_cleanup():
            async with AsyncSessionLocal() as session:
                count = await MetricsHistoryService.cleanup_old_samples(
                    session, days_to_keep=90
                )
                await session.commit()
                return {"deleted": count}

        result = loop.run_until_complete(run_cleanup())
        loop.close()

        logger.info(f"🗑️ Cleanup complete: {result['deleted']} old samples deleted")
        return result

    except Exception as e:
        logger.error(f"❌ Task error in cleanup_old_data: {e}", exc_info=True)
        raise


logger.info("✅ Monitoring tasks module loaded")
