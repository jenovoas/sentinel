"""
Analytics API Routes - Phase 2
Endpoints for retrieving historical metrics, anomalies, and reports
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.monitoring import Anomaly, MetricSample, AnomalyType, SeverityLevel
from app.services.metrics_history import MetricsHistoryService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/metrics/recent")
async def get_recent_metrics(
    limit: int = Query(100, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """Get the last N metric samples"""
    samples = await MetricsHistoryService.get_last_n_samples(db, limit)
    return {
        "count": len(samples),
        "samples": [
            {
                "sampled_at": s.sampled_at,
                "cpu_percent": s.cpu_percent,
                "memory_percent": s.memory_percent,
                "memory_used_mb": s.memory_used_mb,
                "gpu_percent": s.gpu_percent,
                "network_bytes_sent": s.network_bytes_sent,
                "network_bytes_recv": s.network_bytes_recv,
                "db_connections_active": s.db_connections_active,
                "db_locks": s.db_locks,
            }
            for s in samples
        ],
    }


@router.get("/metrics/range")
async def get_metrics_in_range(
    start_time: datetime = Query(..., description="Start time (ISO 8601)"),
    end_time: datetime = Query(..., description="End time (ISO 8601)"),
    limit: int = Query(10000, ge=1, le=100000),
    db: AsyncSession = Depends(get_db),
):
    """Get metric samples in a time range"""
    samples = await MetricsHistoryService.get_samples_in_range(db, start_time, end_time, limit)
    return {
        "period": f"{start_time} to {end_time}",
        "count": len(samples),
        "samples": [
            {
                "sampled_at": s.sampled_at,
                "cpu_percent": s.cpu_percent,
                "memory_percent": s.memory_percent,
                "memory_used_mb": s.memory_used_mb,
                "gpu_percent": s.gpu_percent,
                "network_bytes_sent": s.network_bytes_sent,
                "network_bytes_recv": s.network_bytes_recv,
                "db_connections_active": s.db_connections_active,
                "db_locks": s.db_locks,
            }
            for s in samples
        ],
    }


@router.get("/statistics")
async def get_statistics(
    hours: int = Query(24, ge=1, le=8760),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregate statistics for the last N hours"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    stats = await MetricsHistoryService.compute_statistics(db, start_time, end_time)
    return stats


@router.get("/anomalies")
async def get_anomalies(
    hours: int = Query(24, ge=1, le=8760),
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity"),
    anomaly_type: Optional[AnomalyType] = Query(None, description="Filter by anomaly type"),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """Get anomalies detected in the last N hours"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    anomalies = await MetricsHistoryService.get_anomalies_in_range(
        db, start_time, end_time, anomaly_type, severity, limit
    )

    return {
        "period": f"last {hours} hours",
        "count": len(anomalies),
        "anomalies": [
            {
                "id": str(a.id),
                "detected_at": a.detected_at,
                "type": a.anomaly_type.value,
                "severity": a.severity.value,
                "title": a.title,
                "description": a.description,
                "metric_value": a.metric_value,
                "threshold_value": a.threshold_value,
                "is_resolved": a.is_resolved,
                "resolved_at": a.resolved_at,
            }
            for a in anomalies
        ],
    }


@router.get("/anomalies/{anomaly_id}")
async def get_anomaly_detail(
    anomaly_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific anomaly"""
    from sqlalchemy import select

    stmt = select(Anomaly).where(Anomaly.id == anomaly_id)
    result = await db.execute(stmt)
    anomaly = result.scalar_one_or_none()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    return {
        "id": str(anomaly.id),
        "detected_at": anomaly.detected_at,
        "type": anomaly.anomaly_type.value,
        "severity": anomaly.severity.value,
        "title": anomaly.title,
        "description": anomaly.description,
        "metric_value": anomaly.metric_value,
        "threshold_value": anomaly.threshold_value,
        "context_data": anomaly.context_data,
        "is_resolved": anomaly.is_resolved,
        "resolved_at": anomaly.resolved_at,
        "resolution_notes": anomaly.resolution_notes,
        "ai_analysis": anomaly.ai_analysis,
    }


@router.patch("/anomalies/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: str,
    resolution_notes: str = Query(..., min_length=1, max_length=500),
    db: AsyncSession = Depends(get_db),
):
    """Mark an anomaly as resolved"""
    from sqlalchemy import select

    stmt = select(Anomaly).where(Anomaly.id == anomaly_id)
    result = await db.execute(stmt)
    anomaly = result.scalar_one_or_none()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly.is_resolved = True
    anomaly.resolved_at = datetime.utcnow()
    anomaly.resolution_notes = resolution_notes

    await db.flush()

    return {
        "id": str(anomaly.id),
        "is_resolved": True,
        "resolved_at": anomaly.resolved_at,
    }


@router.get("/export/metrics")
async def export_metrics_csv(
    hours: int = Query(24, ge=1, le=8760),
    db: AsyncSession = Depends(get_db),
):
    """Export metrics to CSV format"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    metrics, _ = await MetricsHistoryService.get_metrics_for_export(db, start_time, end_time)

    # Build CSV
    csv_lines = [
        "sampled_at,cpu_percent,memory_percent,memory_used_mb,memory_total_mb,gpu_percent,gpu_memory_percent,gpu_temperature,network_bytes_sent,network_bytes_recv,network_packets_sent,network_packets_recv,db_connections_total,db_connections_active,db_locks,db_size_bytes"
    ]

    for m in metrics:
        csv_lines.append(
            f"{m.sampled_at},{m.cpu_percent},{m.memory_percent},{m.memory_used_mb},{m.memory_total_mb},{m.gpu_percent},{m.gpu_memory_percent},{m.gpu_temperature},{m.network_bytes_sent},{m.network_bytes_recv},{m.network_packets_sent},{m.network_packets_recv},{m.db_connections_total},{m.db_connections_active},{m.db_locks},{m.db_size_bytes}"
        )

    return {
        "format": "csv",
        "count": len(metrics),
        "data": "\n".join(csv_lines),
    }


@router.get("/export/anomalies")
async def export_anomalies_json(
    hours: int = Query(24, ge=1, le=8760),
    db: AsyncSession = Depends(get_db),
):
    """Export anomalies to JSON format"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)

    anomalies = await MetricsHistoryService.get_anomalies_in_range(db, start_time, end_time)

    return {
        "format": "json",
        "period": f"last {hours} hours",
        "count": len(anomalies),
        "anomalies": [
            {
                "id": str(a.id),
                "detected_at": a.detected_at,
                "type": a.anomaly_type.value,
                "severity": a.severity.value,
                "title": a.title,
                "description": a.description,
                "metric_value": a.metric_value,
                "threshold_value": a.threshold_value,
                "context_data": a.context_data,
                "is_resolved": a.is_resolved,
                "resolved_at": a.resolved_at,
            }
            for a in anomalies
        ],
    }


logger.info("✅ Analytics router initialized")
