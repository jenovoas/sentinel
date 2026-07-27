"""
Unit Tests for Authentication Security

Tests the password hashing and verification utilities, as well as JWT token generation.
"""

from datetime import datetime, timedelta
import jwt
import pytest
from app.security.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.config import get_settings

settings = get_settings()


def test_password_hashing():
    """Verify that password hashing works and is non-reversible"""
    password = "secret_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")  # bcrypt prefix
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """Verify that password verification fails for incorrect passwords"""
    password = "secret_password_123"
    wrong_password = "wrong_password_123"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False


def test_empty_password():
    """Verify behavior with empty strings"""
    password = ""
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


def test_password_consistency():
    """Verify that same password results in different hashes (due to salt) but both verify"""
    password = "consistent_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    assert hash1 != hash2
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_long_password():
    """Verify behavior with long passwords"""
    password = "a" * 100
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_special_characters():
    """Verify behavior with special and unicode characters"""
    password = "P@$$w0rd_with_ñ_and_🚀"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True


def test_create_access_token_success():
    """Verify that create_access_token creates a valid JWT with correct claims"""
    data = {"sub": "testuser", "role": "admin"}
    token = create_access_token(data=data)

    # Decode the token and verify content
    decoded = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "admin"
    assert "exp" in decoded

    # Verify expiration is approximately settings.access_token_expire_minutes in the future
    expected_expiry = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    token_expiry = datetime.utcfromtimestamp(decoded["exp"])
    # Allow a small buffer of 5 seconds for test execution overhead
    assert abs((token_expiry - expected_expiry).total_seconds()) < 5


def test_create_access_token_custom_expiry():
    """Verify that custom expires_delta is respected when creating an access token"""
    data = {"sub": "tempuser"}
    custom_delta = timedelta(minutes=15)
    token = create_access_token(data=data, expires_delta=custom_delta)

    decoded = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    assert decoded["sub"] == "tempuser"
    assert "exp" in decoded

    expected_expiry = datetime.utcnow() + custom_delta
    token_expiry = datetime.utcfromtimestamp(decoded["exp"])
    assert abs((token_expiry - expected_expiry).total_seconds()) < 5


def test_create_access_token_invalid_signature():
    """Verify that decoding with a different secret key raises InvalidSignatureError"""
    data = {"sub": "testuser"}
    token = create_access_token(data=data)

    with pytest.raises(jwt.exceptions.InvalidSignatureError):
        jwt.decode(
            token,
            "wrong_secret_key_123_abc_456_def_ghi",
            algorithms=[settings.algorithm]
        )


def test_create_refresh_token_success():
    """Verify that create_refresh_token creates a token with longer expiry and type claim"""
    data = {"sub": "refreshuser"}
    token = create_refresh_token(data=data)

    decoded = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    assert decoded["sub"] == "refreshuser"
    assert decoded["type"] == "refresh"
    assert "exp" in decoded

    # Verify expiration is approximately settings.refresh_token_expire_days in the future
    expected_expiry = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    token_expiry = datetime.utcfromtimestamp(decoded["exp"])
    assert abs((token_expiry - expected_expiry).total_seconds()) < 5
