# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Security module for Sentinel application.

Handles all security-related functionality including:
- Password hashing and verification with bcrypt
- JWT token creation and validation
- FastAPI dependencies for authentication
- Async-compatible authentication flow with AsyncSession
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError as JWTError
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.organization import Organization
from app.models.user import User, UserRole

settings = get_settings()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = timedelta(minutes=10)
EXPECTED_ALEMBIC_HEADS = frozenset({"20261029_merge_all_heads"})

# ============================================================================
# PASSWORD HASHING
# ============================================================================

def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    pwd_bytes = password.encode("utf-8")
    if len(pwd_bytes) > 72:
        raise ValueError("password must not exceed 72 UTF-8 bytes")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        pwd_bytes = plain_password.encode("utf-8")
        if len(pwd_bytes) > 72:
            return False
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


class _PwdContextCompat:
    @staticmethod
    def hash(secret: str) -> str:
        return get_password_hash(secret)

    @staticmethod
    def verify(secret: str, hashed: str) -> bool:
        return verify_password(secret, hashed)


pwd_context = _PwdContextCompat()


# ============================================================================
# JWT TOKEN HANDLING
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(user: User) -> str:
    """Issue the fixed ten-minute JWT contract shared with Sentinel Cortex."""
    now = datetime.now(timezone.utc)
    role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
    claims = {
        "sub": str(user.id),
        "tenant_id": str(user.organization_id),
        "role": role,
        "is_superuser": user.is_superuser,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "exp": now + ACCESS_TOKEN_TTL,
    }
    return jwt.encode(claims, settings.secret_key, algorithm=JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary of claims to encode in the token
        
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )


# ============================================================================
# ASYNC AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate the JWT against the active user, tenant, and organization."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[JWT_ALGORITHM],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={
                "require": [
                    "sub", "tenant_id", "role", "is_superuser", "iss", "aud", "iat", "exp"
                ]
            },
        )
        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])
        token_role = UserRole(payload["role"])
        is_superuser = payload["is_superuser"]
        issued_at, expires_at = payload["iat"], payload["exp"]
        if (
            type(is_superuser) is not bool
            or type(issued_at) is not int
            or type(expires_at) is not int
            or expires_at - issued_at != int(ACCESS_TOKEN_TTL.total_seconds())
        ):
            raise ValueError("invalid token claims")
    except (JWTError, KeyError, TypeError, ValueError):
        raise _invalid_credentials()

    await ensure_schema_current(db)
    await set_tenant_context(db, tenant_id)
    result = await db.execute(
        select(User).where(User.id == user_id, User.organization_id == tenant_id)
    )
    user = result.scalars().first()
    if user is None or not user.is_active:
        raise _invalid_credentials()

    organization = await db.get(Organization, tenant_id)
    if organization is None or not organization.is_active:
        raise _invalid_credentials()

    actual_role = user.role if isinstance(user.role, UserRole) else UserRole(user.role)
    if actual_role != token_role or user.is_superuser is not is_superuser:
        raise _invalid_credentials()
    return user


async def set_tenant_context(db: AsyncSession, tenant_id: UUID | str) -> None:
    """Set transaction-local PostgreSQL RLS context before tenant queries."""
    await db.execute(
        text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
        {"tenant_id": str(tenant_id)},
    )


async def ensure_schema_current(db: AsyncSession) -> None:
    """Fail closed unless the database matches this main branch's Alembic head."""
    try:
        result = await db.execute(text("SELECT version_num FROM alembic_version"))
        if frozenset(result.scalars().all()) != EXPECTED_ALEMBIC_HEADS:
            raise HTTPException(status_code=503, detail="Database schema is not current")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database schema is unavailable") from exc


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.
    
    Args:
        current_user: Current authenticated user (from get_current_user)
        
    Returns:
        TokenData: User information if active
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    return current_user


async def get_current_user_model(
    current_user: User = Depends(get_current_user),
) -> User:
    """Compatibility dependency; authentication already returns the User model."""
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Restricts access to users with the ADMIN role.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser role required",
        )
    return current_user


__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "get_current_user",
    "get_current_active_user",
    "get_current_user_model",
    "get_current_admin_user",
    "get_current_superuser",
    "oauth2_scheme",
    "pwd_context",
]
