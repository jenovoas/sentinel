"""
Security Schemas

Data models for security-related operations
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SanitizationResult(BaseModel):
    """Result of telemetry sanitization"""
    is_safe: bool = Field(..., description="Whether the input is safe for AI processing")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    blocked_patterns: List[str] = Field(default_factory=list, description="List of blocked patterns found")
    safe_prompt: Optional[str] = Field(None, description="Sanitized version of the prompt")
    original_prompt: str = Field(..., description="Original unsanitized prompt")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_safe": False,
                "confidence": 0.2,
                "blocked_patterns": ["DROP TABLE", "rm -rf"],
                "safe_prompt": None,
                "original_prompt": "Error: DROP TABLE users; --"
            }
        }


class SanitizedLog(BaseModel):
    """Sanitized log entry safe for AI processing"""
    original: Dict = Field(..., description="Original log data")
    safe_for_llm: bool = Field(..., description="Whether safe to send to LLM")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Safety confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Sanitization timestamp")
    blocked_patterns: List[str] = Field(default_factory=list, description="Patterns that were blocked")
    
    class Config:
        json_schema_extra = {
            "example": {
                "original": {"level": "ERROR", "message": "Database error"},
                "safe_for_llm": True,
                "confidence": 0.95,
                "timestamp": "2025-12-15T21:00:00Z",
                "blocked_patterns": []
            }
        }
