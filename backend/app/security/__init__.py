"""
Security Module

Provides security utilities including:
- Telemetry sanitization (AI prompt injection prevention)
- Input validation
- Security schemas
"""

from .telemetry_sanitizer import TelemetrySanitizer, SanitizationResult
from .schemas import SanitizedLog
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_active_user,
    get_current_user_model,
    get_current_admin_user,
    oauth2_scheme,
    pwd_context,
)

__all__ = [
    "TelemetrySanitizer",
    "SanitizationResult",
    "SanitizedLog",
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_user_model",
    "get_current_admin_user",
    "oauth2_scheme",
    "pwd_context",
]
