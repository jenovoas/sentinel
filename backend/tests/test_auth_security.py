# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Pruebas unitarias de seguridad de autenticación

Prueba las utilidades de hash y verificación de contraseñas.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security.auth import get_password_hash, verify_password

client = TestClient(app)

def test_unauthenticated_endpoints_return_401():
    """Comprueba que todos los endpoints protegidos recientemente devuelvan 401 No autorizado para solicitudes anónimas."""
    protected = [
        ("POST", "/api/v1/ai/api/v1/ai/query", {"prompt": "test"}),
        ("POST", "/api/v1/users/api/v1/users/", {"username": "test", "password": "pwd", "email": "test@test.com"}),
        ("POST", "/api/v1/tenants/api/v1/tenants/", {"name": "test"}),
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
    """Comprueba que el hash de contraseñas funcione y no sea reversible."""
    password = "secret_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")  # Prefijo de bcrypt.
    assert verify_password(password, hashed) is True

def test_verify_password_failure():
    """Comprueba que la verificación de contraseña falle para contraseñas incorrectas."""
    password = "secret_password_123"
    wrong_password = "wrong_password_123"
    hashed = get_password_hash(password)

    assert verify_password(wrong_password, hashed) is False

def test_empty_password():
    """Comprueba el comportamiento con cadenas vacías."""
    password = ""
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True

def test_password_consistency():
    """Comprueba que una misma contraseña produzca hashes diferentes debido a la sal, pero que ambos se verifiquen."""
    password = "consistent_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    assert hash1 != hash2
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True

def test_long_password():
    """Comprueba el comportamiento con contraseñas largas."""
    password = "a" * 100
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True

def test_special_characters():
    """Comprueba el comportamiento con caracteres especiales y Unicode."""
    password = "P@$$w0rd_with_ñ_and_🚀"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
