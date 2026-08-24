# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Unit Tests for Authentication Security

Tests the password hashing and verification utilities.
"""

import pytest
from app.security.auth import get_password_hash, verify_password
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_unauthenticated_endpoints_return_401():
    """Verify that all newly protected endpoints return 401 Unauthorized for anonymous requests"""
    protected = [
        ("POST", "/api/v1/ai/api/v1/ai/query", {"prompt": "test"}),
        ("POST", "/api/v1/users/api/v1/users/", {"username": "test", "password": "pwd", "email": "test@test.com"}),
        ("POST", "/api/v1/tenants/api/v1/tenants/", {"name": "test", "slug": "test-tenant"}),
        ("POST", "/api/v1/backup/trigger", {}),
        ("POST", "/api/v1/failsafe/trigger", {"playbook": "Incident Response", "wait_seconds": 10, "details": {}}),
        ("GET", "/api/v1/analytics/api/v1/analytics/metrics/recent"),
        ("GET", "/api/v1/analytics/api/v1/analytics/metrics/range"),
        ("GET", "/api/v1/analytics/api/v1/analytics/statistics"),
        ("GET", "/api/v1/analytics/api/v1/analytics/anomalies"),
        ("GET", "/api/v1/analytics/api/v1/analytics/export/metrics"),
        ("GET", "/api/v1/analytics/api/v1/analytics/export/anomalies"),
        ("GET", "/api/v1/analytics/api/v1/analytics/storage/summary"),
        ("GET", "/api/v1/metrics"),
    ]
    for entry in protected:
        if len(entry) == 3:
            method, path, data = entry
        else:
            method, path = entry
            data = None
        if method == "POST":
            response = client.post(path, json=data)
        elif method == "GET":
            response = client.get(path)
        assert response.status_code == 401, f"{method} {path} should require authentication, got {response.status_code}"

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
