from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.models.user import User, UserRole
from app.routers.tenants import router as tenants_router
from app.routers.users import router as users_router
from app.security.auth import get_current_user


def install_user_and_db(app, user, db):
    async def override_db():
        yield db

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = override_db


def mock_result(entity):
    result = MagicMock()
    result.scalars.return_value.first.return_value = entity
    return result


@pytest.mark.parametrize(
    ("role", "expected_status"),
    [(UserRole.MEMBER, 403), (UserRole.ADMIN, 200)],
)
def test_only_admin_can_change_user_active_flag(role, expected_status):
    organization_id = uuid4()
    current_user = User(
        id=uuid4(), organization_id=organization_id, tenant_id=organization_id,
        email="operator@example.com", username="operator", password_hash="unused",
        first_name="Operator", last_name="User", role=role, is_superuser=False,
        is_active=True,
    )
    target = User(
        id=uuid4(), organization_id=organization_id, tenant_id=organization_id,
        email="target@example.com", username="target", password_hash="unused",
        first_name="Target", last_name="User", role=UserRole.MEMBER,
        is_superuser=False, is_active=True, created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db = AsyncMock()
    db.execute.return_value = mock_result(target)
    db.add = MagicMock()
    app = FastAPI()
    app.include_router(users_router)
    install_user_and_db(app, current_user, db)

    response = TestClient(app).put(f"/api/v1/users/{target.id}", json={"is_active": False})

    assert response.status_code == expected_status
    if expected_status == 403:
        assert target.is_active is True
        db.commit.assert_not_awaited()
    else:
        assert target.is_active is False
        db.commit.assert_awaited_once()
    app.dependency_overrides.clear()


def test_organization_admin_cannot_create_or_delete_global_tenants():
    organization_id = uuid4()
    organization_admin = User(
        id=uuid4(), organization_id=organization_id, tenant_id=organization_id,
        email="admin@example.com", username="admin", password_hash="unused",
        first_name="Org", last_name="Admin", role=UserRole.ADMIN,
        is_superuser=False, is_active=True,
    )
    db = AsyncMock()
    app = FastAPI()
    app.include_router(tenants_router)
    install_user_and_db(app, organization_admin, db)
    client = TestClient(app)

    created = client.post("/api/v1/tenants/", json={"name": "Other", "slug": "other"})
    deleted = client.delete(f"/api/v1/tenants/{uuid4()}")

    assert created.status_code == 403
    assert deleted.status_code == 403
    db.execute.assert_not_awaited()
    app.dependency_overrides.clear()
