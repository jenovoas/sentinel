from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.monitoring import SeverityLevel

class SecurityAlertBase(BaseModel):
    alert_type: str = Field(..., example="execve_watchdog")
    severity: SeverityLevel = Field(default=SeverityLevel.WARNING)
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=1000)
    port: Optional[int] = None
    protocol: Optional[str] = Field(None, max_length=10)
    remote_ip: Optional[str] = Field(None, max_length=45)
    local_process: Optional[str] = Field(None, max_length=255)
    context_data: Optional[Dict[str, Any]] = None

class SecurityAlertCreate(SecurityAlertBase):
    pass

class SecurityAlertUpdate(BaseModel):
    is_investigated: Optional[bool] = None
    investigation_notes: Optional[str] = Field(None, max_length=1000)

class SecurityAlertResponse(SecurityAlertBase):
    id: UUID
    detected_at: datetime
    is_investigated: bool
    investigation_notes: Optional[str] = None

    class Config:
        from_attributes = True
