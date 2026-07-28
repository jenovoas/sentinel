# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Unit Tests for Authentication Security

Tests the password hashing and verification utilities.
"""

import pytest
from app.security.auth import get_password_hash, verify_password

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
