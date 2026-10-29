"""
Security module for Sentinel application.

Handles all security-related functionality including:
- Password hashing and verification with bcrypt
- JWT token creation and validation
- FastAPI dependencies for authentication
- Async-compatible authentication flow with AsyncSession
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from datetime import timedelta
from typing import Optional

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.security.auth import (
    create_access_token as create_authenticated_access_token,
    get_current_user as get_authenticated_user,
)

# ============================================================================
# PASSWORD HASHING
# ============================================================================

# Context for password hashing and verification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    if len(password.encode("utf-8")) > 72:
        raise ValueError("password must not exceed 72 UTF-8 bytes")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    if len(plain_password.encode("utf-8")) > 72:
        return False
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN HANDLING
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """Keep the legacy import path on the canonical short-lived JWT contract."""
    if expires_delta is not None:
        raise ValueError("custom access-token lifetimes are not supported")
    return create_authenticated_access_token(user)


# ============================================================================
# ASYNC AUTHENTICATION DEPENDENCIES
# ============================================================================

async def get_current_user(
    current_user: User = Depends(get_authenticated_user),
) -> User:
    """Keep legacy imports on the canonical tenant- and role-checked verifier."""
    return current_user


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


__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "get_current_user",
    "get_current_active_user",
    "oauth2_scheme",
    "pwd_context",
]
