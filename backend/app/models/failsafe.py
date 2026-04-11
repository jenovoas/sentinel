"""
Sentinel Fail-Safe Execution Model - Tracking automated remediation
SQLAlchemy 2.0 + PostgreSQL UUID support
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, DateTime, func, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FailSafeStatus(str, PyEnum):
    """Status of a playbook execution"""
    IDLE = "idle"
    WAITING = "waiting"
    TRIGGERED = "triggered"
    SUCCESS = "success"
    FAILED = "failed"


class FailSafeExecution(Base):
    """Historical record of fail-safe playbook executions"""
    __tablename__ = "failsafe_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Playbook details
    playbook: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[FailSafeStatus] = mapped_column(
        Enum(FailSafeStatus, name="failsafe_status_enum"),
        default=FailSafeStatus.TRIGGERED,
        nullable=False,
        index=True
    )

    # Trigger info
    triggered_by: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)

    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Context and Outcome
    context_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    outcome: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    def __repr__(self) -> str:
        return f"<FailSafeExecution(playbook='{self.playbook}', status='{self.status}', started_at='{self.started_at}')>"
