import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class FailSafeExecution(Base):
    """Tracks execution of fail-safe playbooks"""
    __tablename__ = "failsafe_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    playbook: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # triggered, success, failed, waiting

    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    triggered_by: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)

    outcome: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    context_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<FailSafeExecution(playbook={self.playbook}, status={self.status}, triggered_at={self.triggered_at})>"
