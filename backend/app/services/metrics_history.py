"""
Historical Metrics Storage Service
Stores all metrics samples for Phase 2 analysis and Phase 3 AI integration
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.monitoring import MetricSample, Anomaly, AnomalyType, SeverityLevel
from app.services.monitoring import get_dashboard_snapshot


logger = logging.getLogger(__name__)


class MetricsHistoryService:
    """Manage historical storage and retrieval of metrics for analysis"""

    @staticmethod
    async def store_metric_sample(
        session: AsyncSession,
        cpu: float,
        memory: float,
        memory_used_mb: float,
        memory_total_mb: float,
        network_bytes_sent: int,
        network_bytes_recv: int,
        network_packets_sent: int,
        network_packets_recv: int,
        db_connections_total: int,
        db_connections_active: int,
        db_locks: int,
        db_size_bytes: int,
        gpu_percent: Optional[float] = None,
        gpu_memory_percent: Optional[float] = None,
        gpu_temperature: Optional[float] = None,
        wifi_ssid: Optional[str] = None,
        wifi_signal: Optional[int] = None,
        wifi_connected: bool = False,
        metadata: Optional[dict] = None,
    ) -> MetricSample:
        """
        Store a complete metric sample.

        Args:
            session: Database session
            cpu: CPU usage percentage
            memory: Memory usage percentage
            memory_used_mb: Used memory in MB
            memory_total_mb: Total memory in MB
            network_bytes_sent: Network bytes sent
            network_bytes_recv: Network bytes received
            network_packets_sent: Network packets sent
            network_packets_recv: Network packets received
            db_connections_total: Total DB connections
            db_connections_active: Active DB connections
            db_locks: Number of DB locks
            db_size_bytes: Database size in bytes
            gpu_percent: GPU usage (optional)
            gpu_memory_percent: GPU memory usage (optional)
            gpu_temperature: GPU temperature (optional)
            wifi_ssid: WiFi network name (optional)
            wifi_signal: WiFi signal strength 0-100 (optional)
            wifi_connected: WiFi connection status (optional)
            metadata: Additional metadata (e.g., app version, environment)

        Returns:
            MetricSample: Created sample record
        """
        sample = MetricSample(
            cpu_percent=cpu,
            memory_percent=memory,
            memory_used_mb=memory_used_mb,
            memory_total_mb=memory_total_mb,
            gpu_percent=gpu_percent,
            gpu_memory_percent=gpu_memory_percent,
            gpu_temperature=gpu_temperature,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv,
            network_packets_sent=network_packets_sent,
            network_packets_recv=network_packets_recv,
            db_connections_total=db_connections_total,
            db_connections_active=db_connections_active,
            db_locks=db_locks,
            db_size_bytes=db_size_bytes,
            wifi_ssid=wifi_ssid,
            wifi_signal=wifi_signal,
            wifi_connected=wifi_connected,
            context_metadata=metadata or {},
        )

        session.add(sample)
        await session.flush()

        return sample


    @staticmethod
    async def get_samples_in_range(
        session: AsyncSession,
        start_time: datetime,
        end_time: datetime,
        limit: int = 10000,
    ) -> List[MetricSample]:
        """
        Get all metric samples in a time range.

        Args:
            session: Database session
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of samples to return

        Returns:
            List of MetricSample records
        """
        stmt = select(MetricSample).where(
            and_(
                MetricSample.sampled_at >= start_time,
                MetricSample.sampled_at <= end_time,
            )
        ).order_by(MetricSample.sampled_at).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def get_last_n_samples(
        session: AsyncSession,
        n: int = 100,
    ) -> List[MetricSample]:
        """Get the last N metric samples"""
        stmt = select(MetricSample).order_by(desc(MetricSample.sampled_at)).limit(n)
        result = await session.execute(stmt)
        samples = result.scalars().all()
        return list(reversed(samples))  # Return in chronological order


    @staticmethod
    async def get_anomalies_in_range(
        session: AsyncSession,
        start_time: datetime,
        end_time: datetime,
        anomaly_type: Optional[AnomalyType] = None,
        severity: Optional[SeverityLevel] = None,
        limit: int = 10000,
    ) -> List[Anomaly]:
        """
        Get anomalies detected in a time range.

        Args:
            session: Database session
            start_time: Start of time range
            end_time: End of time range
            anomaly_type: Filter by anomaly type (optional)
            severity: Filter by severity level (optional)
            limit: Maximum number of records

        Returns:
            List of Anomaly records
        """
        conditions = [
            and_(
                Anomaly.detected_at >= start_time,
                Anomaly.detected_at <= end_time,
            )
        ]

        if anomaly_type:
            conditions.append(Anomaly.anomaly_type == anomaly_type)

        if severity:
            conditions.append(Anomaly.severity == severity)

        stmt = select(Anomaly).where(and_(*conditions)).order_by(desc(Anomaly.detected_at)).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()


    @staticmethod
    async def compute_statistics(
        session: AsyncSession,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict:
        """
        Compute aggregate statistics for a time period.

        Args:
            session: Database session
            start_time: Start of period
            end_time: End of period

        Returns:
            Dictionary with statistics
        """
        samples = await MetricsHistoryService.get_samples_in_range(
            session, start_time, end_time, limit=100000
        )

        if not samples:
            return {
                'period': f"{start_time} to {end_time}",
                'sample_count': 0,
                'error': 'No samples found for period',
            }

        # Extract arrays
        cpu_values = [s.cpu_percent for s in samples]
        memory_values = [s.memory_percent for s in samples]
        network_bytes = [s.network_bytes_sent + s.network_bytes_recv for s in samples]
        db_connections = [s.db_connections_active for s in samples]

        import numpy as np

        stats = {
            'period': f"{start_time} to {end_time}",
            'sample_count': len(samples),
            'sample_interval_seconds': 15,  # Assuming 15-second collection
            'cpu': {
                'mean': float(np.mean(cpu_values)),
                'max': float(np.max(cpu_values)),
                'min': float(np.min(cpu_values)),
                'std': float(np.std(cpu_values)),
                'p95': float(np.percentile(cpu_values, 95)),
                'p99': float(np.percentile(cpu_values, 99)),
            },
            'memory': {
                'mean': float(np.mean(memory_values)),
                'max': float(np.max(memory_values)),
                'min': float(np.min(memory_values)),
                'std': float(np.std(memory_values)),
                'p95': float(np.percentile(memory_values, 95)),
                'p99': float(np.percentile(memory_values, 99)),
            },
            'network': {
                'total_bytes': int(np.sum(network_bytes)),
                'mean_bytes_per_sample': float(np.mean(network_bytes)),
                'max_bytes_per_sample': float(np.max(network_bytes)),
            },
            'database': {
                'avg_connections': float(np.mean(db_connections)),
                'max_connections': int(np.max(db_connections)),
            },
            'anomalies_detected': await MetricsHistoryService._count_anomalies(
                session, start_time, end_time
            ),
        }

        return stats


    @staticmethod
    async def _count_anomalies(
        session: AsyncSession,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict:
        """Count anomalies by type and severity"""
        stmt = select(Anomaly).where(
            and_(
                Anomaly.detected_at >= start_time,
                Anomaly.detected_at <= end_time,
            )
        )

        result = await session.execute(stmt)
        anomalies = result.scalars().all()

        counts = {
            'total': len(anomalies),
            'by_type': {},
            'by_severity': {
                'info': 0,
                'warning': 0,
                'critical': 0,
            },
        }

        for anomaly in anomalies:
            # Count by type
            atype = anomaly.anomaly_type.value
            if atype not in counts['by_type']:
                counts['by_type'][atype] = 0
            counts['by_type'][atype] += 1

            # Count by severity
            severity = anomaly.severity.value
            counts['by_severity'][severity] += 1

        return counts


    @staticmethod
    async def get_metrics_for_export(
        session: AsyncSession,
        start_time: datetime,
        end_time: datetime,
    ) -> Tuple[List[MetricSample], List[Anomaly]]:
        """
        Get metrics and anomalies for export to files.

        Returns:
            (metrics_list, anomalies_list)
        """
        metrics = await MetricsHistoryService.get_samples_in_range(
            session, start_time, end_time, limit=100000
        )

        anomalies = await MetricsHistoryService.get_anomalies_in_range(
            session, start_time, end_time, limit=10000
        )

        return metrics, anomalies


    @staticmethod
    async def cleanup_old_samples(
        session: AsyncSession,
        days_to_keep: int = 90,
    ) -> int:
        """
        Delete metric samples older than N days (keep last 90 days by default).

        Args:
            session: Database session
            days_to_keep: Number of days of data to retain

        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        stmt = select(MetricSample).where(
            MetricSample.sampled_at < cutoff_date
        )

        result = await session.execute(stmt)
        old_samples = result.scalars().all()

        for sample in old_samples:
            await session.delete(sample)

        await session.flush()
        count = len(old_samples)

        logger.info(f"🗑️ Cleaned up {count} samples older than {days_to_keep} days")
        return count


logger.info("✅ MetricsHistoryService initialized for Phase 2 analytics")
