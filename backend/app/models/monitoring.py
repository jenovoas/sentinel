"""
Sentinel Monitoring Models - Historical data, anomalies, security alerts
Phase 2: Data aggregation for AI analysis (Phase 3)
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Float, DateTime, Integer, ForeignKey, Enum, func, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnomalyType(str, PyEnum):
    """Types of anomalies detected"""
    CPU_SPIKE = "cpu_spike"           # CPU > 90% for >2min
    MEMORY_SPIKE = "memory_spike"     # Memory > 85% sustained
    NETWORK_SPIKE = "network_spike"   # Unusual network activity
    PORT_OPEN = "port_open"           # New listening port
    CONNECTION_SURGE = "conn_surge"   # DB connections spike
    LOCK_DETECTED = "lock_detected"   # DB deadlock/lock detected
    QUERY_SLOW = "query_slow"         # Query >60 seconds
    GPU_OVERHEAT = "gpu_overheat"     # GPU temp > 85°C
    UNAUTHORIZED_ACCESS = "unauth_access"  # Failed login attempts


class SeverityLevel(str, PyEnum):
    """Alert severity"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricSample(Base):
    """Store all metric samples for historical analysis"""
    __tablename__ = "metric_samples"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Timestamp
    sampled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # System Metrics
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_percent: Mapped[float] = mapped_column(Float, nullable=False)
    memory_used_mb: Mapped[float] = mapped_column(Float, nullable=False)
    memory_total_mb: Mapped[float] = mapped_column(Float, nullable=False)

    # GPU (if available)
    gpu_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gpu_memory_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gpu_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Network
    network_bytes_sent: Mapped[int] = mapped_column(Integer, nullable=False)
    network_bytes_recv: Mapped[int] = mapped_column(Integer, nullable=False)
    network_packets_sent: Mapped[int] = mapped_column(Integer, nullable=False)
    network_packets_recv: Mapped[int] = mapped_column(Integer, nullable=False)

    # Database
    db_connections_total: Mapped[int] = mapped_column(Integer, nullable=False)
    db_connections_active: Mapped[int] = mapped_column(Integer, nullable=False)
    db_locks: Mapped[int] = mapped_column(Integer, nullable=False)
    db_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata for AI analysis
    context_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<MetricSample(sampled_at={self.sampled_at}, cpu={self.cpu_percent}%, mem={self.memory_percent}%)>"


class Anomaly(Base):
    """Detected anomalies for analysis"""
    __tablename__ = "anomalies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Detection time
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Anomaly details
    anomaly_type: Mapped[AnomalyType] = mapped_column(
        Enum(AnomalyType, name="anomaly_type_enum"),
        nullable=False,
        index=True
    )

    severity: Mapped[SeverityLevel] = mapped_column(
        Enum(SeverityLevel, name="severity_level_enum"),
        default=SeverityLevel.WARNING,
        nullable=False
    )

    # Description and context
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Data points that triggered anomaly
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    context_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Resolution tracking
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Link to AI analysis (for Phase 3)
    ai_analysis: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Anomaly({self.anomaly_type}, severity={self.severity}, detected={self.detected_at})>"


class SecurityAlert(Base):
    """Security-specific alerts: ports, connections, auth"""
    __tablename__ = "security_alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Alert time
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Alert type
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)  # 'port_open', 'suspicious_connection', 'auth_failure', etc
    severity: Mapped[SeverityLevel] = mapped_column(
        Enum(SeverityLevel, name="severity_level_enum"),
        default=SeverityLevel.WARNING,
        nullable=False
    )

    # Details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Specific data
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    protocol: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # TCP, UDP
    remote_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    local_process: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Full context
    context_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Status
    is_investigated: Mapped[bool] = mapped_column(Boolean, default=False)
    investigation_notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    def __repr__(self) -> str:
        return f"<SecurityAlert({self.alert_type}, severity={self.severity})>"


class SystemReport(Base):
    """Automated daily/weekly reports for trend analysis"""
    __tablename__ = "system_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Report details
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'daily', 'weekly', 'monthly'
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Metrics summary
    cpu_avg: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_max: Mapped[float] = mapped_column(Float, nullable=False)
    cpu_min: Mapped[float] = mapped_column(Float, nullable=False)

    memory_avg: Mapped[float] = mapped_column(Float, nullable=False)
    memory_max: Mapped[float] = mapped_column(Float, nullable=False)

    network_bytes_total: Mapped[int] = mapped_column(Integer, nullable=False)

    # Anomalies in period
    anomalies_count: Mapped[int] = mapped_column(Integer, default=0)
    critical_anomalies_count: Mapped[int] = mapped_column(Integer, default=0)
    security_alerts_count: Mapped[int] = mapped_column(Integer, default=0)

    # Full report data (JSON)
    report_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Files generated
    report_files: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {'csv': 'path', 'json': 'path', 'pdf': 'path'}

    def __repr__(self) -> str:
        return f"<SystemReport({self.report_type}, period={self.period_start.date()})>"
