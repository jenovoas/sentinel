from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.routers.gamma import router
from app.security.auth import EXPECTED_ALEMBIC_HEADS, create_access_token
from app.services.guardian_gamma import DecisionType, GuardianGammaService, GuardianSource


PENDING_DECISION = {
    "id": 7,
    "guardian": "beta",
    "type": "anomaly_detected",
    "context": {"event_type": "process"},
    "evidence": {"source": "guardian_beta"},
    "confidence_s60_raw": 8424000,
    "created_at": "2026-10-31T10:00:00",
    "timeout_at": "2026-10-31T10:45:00",
}
CREATE_REQUEST = {
    "guardian": "beta",
    "decision_type": "anomaly_detected",
    "context": PENDING_DECISION["context"],
    "evidence": PENDING_DECISION["evidence"],
    "confidence_s60_raw": PENDING_DECISION["confidence_s60_raw"],
    "timeout_minutes": 45,
}
OPERATIONS = [
    pytest.param(
        "POST", "/decision", CREATE_REQUEST, 201,
        {"decision_id": 7, "status": "pending", "timeout_at": PENDING_DECISION["timeout_at"]},
        id="create",
    ),
    pytest.param("GET", "/pending?limit=1", None, 200, [PENDING_DECISION], id="pending"),
    pytest.param(
        "POST", "/approve/7", {"feedback": "Reviewed"}, 200,
        {"status": "approved", "decision_id": 7}, id="approve",
    ),
    pytest.param(
        "POST", "/deny/7", {"feedback": "Reviewed"}, 200,
        {"status": "denied", "decision_id": 7}, id="deny",
    ),
    pytest.param("POST", "/cleanup", None, 200, {"cleaned_up": 2}, id="cleanup"),
]


def result(rows):
    value = MagicMock()
    value.scalars.return_value.all.return_value = rows
    value.scalars.return_value.first.return_value = rows[0] if rows else None
    return value


@pytest.fixture
def gamma_api():
    organization = Organization(id=uuid4(), name="Acme", slug="acme", is_active=True)
    user = User(
        id=uuid4(), organization_id=organization.id,
        email="reviewer@example.com", username="reviewer", password_hash=None,
        first_name="Gamma", last_name="Reviewer", role=UserRole.ADMIN,
        is_superuser=True, is_active=True,
    )
    db = AsyncMock()
    db.execute.side_effect = [
        result(sorted(EXPECTED_ALEMBIC_HEADS)),
        result([]),  # transaction-local tenant context
        result([user]),
    ]
    db.get.return_value = organization

    async def override_db():
        yield db

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    service = AsyncMock(spec=GuardianGammaService)
    service.create_decision.return_value = 7
    service.get_pending_decisions.return_value = [PENDING_DECISION]
    service.approve_decision.return_value = True
    service.deny_decision.return_value = True
    service.cleanup_expired.return_value = 2
    with patch("app.routers.gamma.GuardianGammaService", return_value=service) as factory:
        with TestClient(app) as client:
            yield client, user, organization, db, service, factory
    app.dependency_overrides.clear()


@pytest.mark.parametrize("method,path,body,success_status,expected_body", OPERATIONS)
@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer invalid"}, {"X-Sentinel-Token": "ingestion-token"}],
    ids=["missing", "invalid-jwt", "ingestion-token-is-not-user-auth"],
)
def test_gamma_rejects_missing_or_invalid_authentication(
    gamma_api, method, path, body, success_status, expected_body, headers
):
    client, _, _, db, _, factory = gamma_api

    response = client.request(method, f"/api/v1/gamma{path}", json=body, headers=headers)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    factory.assert_not_called()
    db.execute.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.parametrize("method,path,body,success_status,expected_body", OPERATIONS)
@pytest.mark.parametrize(
    "role,is_superuser,allowed",
    [
        (UserRole.MEMBER, False, False),
        (UserRole.VIEWER, False, False),
        (UserRole.ADMIN, False, False),
        (UserRole.VIEWER, True, True),
    ],
    ids=["member", "viewer", "admin", "superuser"],
)
def test_gamma_requires_platform_superuser_for_global_operations(
    gamma_api, method, path, body, success_status, expected_body,
    role, is_superuser, allowed,
):
    client, user, _, db, service, factory = gamma_api
    user.role = role
    user.is_superuser = is_superuser
    headers = {"Authorization": f"Bearer {create_access_token(user)}"}

    response = client.request(method, f"/api/v1/gamma{path}", json=body, headers=headers)

    if not allowed:
        assert response.status_code == 403
        factory.assert_not_called()
        db.commit.assert_not_awaited()
        return

    assert response.status_code == success_status


@pytest.mark.parametrize("method,path,body,success_status,expected_body", OPERATIONS)
@pytest.mark.parametrize("inactive_entity", ["user", "organization"])
def test_gamma_rejects_inactive_admin_identity(
    gamma_api, method, path, body, success_status, expected_body, inactive_entity
):
    client, user, organization, db, _, factory = gamma_api
    headers = {"Authorization": f"Bearer {create_access_token(user)}"}
    if inactive_entity == "user":
        user.is_active = False
    else:
        organization.is_active = False

    response = client.request(method, f"/api/v1/gamma{path}", json=body, headers=headers)

    assert response.status_code == 401
    factory.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.parametrize("operation", ["approve", "deny"])
def test_gamma_preserves_not_found_for_authorized_decisions(gamma_api, operation):
    client, user, _, _, service, _ = gamma_api
    getattr(service, f"{operation}_decision").return_value = False

    response = client.post(
        f"/api/v1/gamma/{operation}/7",
        json={"feedback": "Reviewed"},
        headers={"Authorization": f"Bearer {create_access_token(user)}"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Decision not found or already decided"}
    getattr(service, f"{operation}_decision").assert_awaited_once_with(
        decision_id=7, feedback="Reviewed"
    )
