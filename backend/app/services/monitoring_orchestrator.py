"""
Monitoring Orchestration Service - Phase 2
Integrates metrics collection, anomaly detection, and historical storage
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.monitoring import get_dashboard_snapshot
from app.services.anomaly_detector import get_anomaly_detector, save_anomalies
from app.services.metrics_history import MetricsHistoryService


logger = logging.getLogger(__name__)


class MonitoringOrchestrator:
    """
    Orchestrates the complete monitoring pipeline:
    1. Collect metrics
    2. Detect anomalies
    3. Store historical data
    """

    @staticmethod
    async def collect_and_process_metrics(session: AsyncSession) -> Dict[str, Any]:
        """
        Complete monitoring cycle: collect, detect, store.

        Returns:
            Dictionary with collection results and detected anomalies
        """
        try:
            # Step 1: Collect current metrics
            snapshot = await get_dashboard_snapshot()

            # Step 2: Detect anomalies
            detector = await get_anomaly_detector()
            anomalies = await detector.analyze_metrics(
                cpu=snapshot["system"]["cpu_percent"],
                memory=snapshot["system"]["mem_percent"],
                network_bytes=snapshot["network"]["net_bytes_sent"] + snapshot["network"]["net_bytes_recv"],
                gpu=snapshot.get("gpu", {}).get("percent"),
                db_connections=snapshot["db_stats"]["connections_active"],
                db_locks=snapshot["db_stats"]["locks"],
                memory_used_mb=snapshot["system"]["mem_used"] / (1024 * 1024),  # Convert bytes to MB
                memory_total_mb=snapshot["system"]["mem_total"] / (1024 * 1024),  # Convert bytes to MB
            )

            # Step 3: Store metrics sample
            net_stats = snapshot["network"]
            db_stats_info = snapshot["db_stats"]
            wifi_info = net_stats.get("wifi", {})
            
            sample = await MetricsHistoryService.store_metric_sample(
                session,
                cpu=snapshot["system"]["cpu_percent"],
                memory=snapshot["system"]["mem_percent"],
                memory_used_mb=snapshot["system"]["mem_used"] / (1024 * 1024),
                memory_total_mb=snapshot["system"]["mem_total"] / (1024 * 1024),
                network_bytes_sent=net_stats.get("net_bytes_sent", 0),
                network_bytes_recv=net_stats.get("net_bytes_recv", 0),
                network_packets_sent=net_stats.get("net_packets_sent", 0),
                network_packets_recv=net_stats.get("net_packets_recv", 0),
                db_connections_total=db_stats_info.get("connections_total", 0),
                db_connections_active=db_stats_info.get("connections_active", 0),
                db_locks=db_stats_info.get("locks", 0),
                db_size_bytes=db_stats_info.get("db_size_bytes", 0),
                gpu_percent=snapshot.get("gpu", {}).get("percent"),
                gpu_memory_percent=snapshot.get("gpu", {}).get("memory_percent"),
                gpu_temperature=snapshot.get("gpu", {}).get("temperature"),
                wifi_ssid=wifi_info.get("ssid"),
                wifi_signal=wifi_info.get("signal"),
                wifi_connected=wifi_info.get("connected", False),
                metadata={
                    "version": "1.0",
                    "phase": "2-analytics",
                },
            )

            # Step 4: Save anomalies
            if anomalies:
                await save_anomalies(session, anomalies)
                logger.warning(f"⚠️ Detected {len(anomalies)} anomalies")

            # Commit transaction
            await session.commit()

            return {
                "success": True,
                "sample_id": str(sample.id),
                "sampled_at": sample.sampled_at,
                "anomalies_detected": len(anomalies),
                "anomalies": [
                    {
                        "type": a.anomaly_type.value,
                        "severity": a.severity.value,
                        "title": a.title,
                    }
                    for a in anomalies
                ],
            }

        except Exception as e:
            logger.error(f"❌ Error in monitoring pipeline: {e}", exc_info=True)
            await session.rollback()
            return {
                "success": False,
                "error": str(e),
            }


logger.info("✅ MonitoringOrchestrator initialized for Phase 2")
