# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Unit tests for Fail-Safe router endpoints (/api/v1/failsafe).
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.failsafe import router, send_to_n8n
from app.security import get_current_admin_user

app = FastAPI()
app.include_router(router)

# Override admin auth dependency for trigger endpoint tests
async def mock_get_current_admin_user():
    return {"id": "admin_user_1", "email": "admin@example.com", "role": "admin"}

app.dependency_overrides[get_current_admin_user] = mock_get_current_admin_user

client = TestClient(app)


def test_get_failsafe_status():
    response = client.get("/api/v1/failsafe/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert "last_auto_remediation" in data
    assert "active_playbooks" in data
    assert "playbooks" in data
    assert isinstance(data["playbooks"], list)
    assert len(data["playbooks"]) == 6


def test_list_playbooks():
    response = client.get("/api/v1/failsafe/playbooks")
    assert response.status_code == 200
    data = response.json()
    assert "playbooks" in data
    assert len(data["playbooks"]) == 6
    playbook_ids = [p["id"] for p in data["playbooks"]]
    assert "backup_recovery" in playbook_ids
    assert "auto_remediation" in playbook_ids


def test_failsafe_health():
    response = client.get("/api/v1/failsafe/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "n8n_configured" in data
    assert data["playbooks_available"] == 6


def test_trigger_failsafe_success():
    payload = {
        "playbook": "backup_recovery",
        "severity": "high",
        "context": {"backup_id": "1234"},
        "triggered_by": "backup_failed",
        "wait_time_minutes": 5
    }
    response = client.post("/api/v1/failsafe/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["playbook"] == "backup_recovery"
    assert data["wait_time_minutes"] == 5


@pytest.mark.asyncio
async def test_send_to_n8n_success():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        res = await send_to_n8n("backup_recovery", {"test": "data"})
        assert res is True


@pytest.mark.asyncio
async def test_send_to_n8n_invalid_playbook():
    res = await send_to_n8n("unknown_playbook", {"test": "data"})
    assert res is False
