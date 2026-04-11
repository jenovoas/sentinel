from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..models.failsafe import FailSafeStatus


class PlaybookStatusSchema(BaseModel):
    """Status of a playbook execution"""

    name: str
    display_name: str
    status: str
    last_run: Optional[str] = None
    last_outcome: Optional[str] = None
    execution_count: int = 0
    success_rate: float = 0.0


class FailSafeStatusResponse(BaseModel):
    """Aggregated status of the fail-safe layer"""

    status: str
    last_auto_remediation: Optional[str] = None
    active_playbooks: int
    success_rate_30d: float
    total_executions: int
    playbooks: List[PlaybookStatusSchema]


class FailSafeExecutionSchema(BaseModel):
    """Schema for a single execution record"""

    id: str
    playbook: str
    status: FailSafeStatus
    triggered_by: str
    severity: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    outcome: Optional[str] = None

    class Config:
        from_attributes = True
