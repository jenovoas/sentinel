# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Security Module

Provides security utilities including:
- Telemetry sanitization (AI prompt injection prevention)
- Input validation
- Security schemas
"""

from .auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_current_admin_user,
    get_current_user,
    get_current_user_model,
    get_password_hash,
    oauth2_scheme,
    pwd_context,
    verify_password,
)
from .schemas import SanitizedLog
from .telemetry_sanitizer import SanitizationResult, TelemetrySanitizer

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
