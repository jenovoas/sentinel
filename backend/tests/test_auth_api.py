from datetime import datetime, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.auth_main import app as auth_app
from app.database import get_db
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.routers.users import router as users_router
from app.security.auth import EXPECTED_ALEMBIC_HEADS, get_current_user
from app.config import get_settings
from app.services.directory_auth import DirectoryIdentity


def result(rows):
    mock = MagicMock()
    mock.scalars.return_value.first.return_value = rows[0] if rows else None
    mock.scalars.return_value.all.return_value = rows
    return mock


def identity(role=UserRole.MEMBER, *, active=True, org_active=True):
    organization_id = uuid4()
    organization = Organization(
        id=organization_id, name="Acme", slug="acme", is_active=org_active
    )
    user = User(
        id=uuid4(),
        organization_id=organization_id,
        email="user@example.com",
        username="user",
        directory_id="00000000-0000-4000-8000-000000000001",
        password_hash=None,
        first_name="Test",
        last_name="User",
        created_at=datetime.now(timezone.utc),
        role=role,
        is_superuser=False,
        is_active=active,
    )
    return organization, user


def install_db_override(app, db):
    async def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db


def login_with(organization, user):
    db = AsyncMock()
    db.execute.side_effect = [
        result(sorted(EXPECTED_ALEMBIC_HEADS)),  # alembic_version
        result([organization]),
        result([]),  # transaction-local RLS setting
        result([user]),
    ]
    install_db_override(auth_app, db)
    identity = DirectoryIdentity(
        directory_id=user.directory_id,
        user_principal_name=user.email,
        email=user.email,
        display_name="Test User",
        sam_account_name=user.username,
        member_of=frozenset(),
    )
    with patch(
        "app.routers.auth.authenticate_directory_user",
        new=AsyncMock(return_value=identity),
    ):
        response = TestClient(auth_app).post(
            "/api/v1/auth/login",
            data={
                "organization_slug": organization.slug,
                "username": user.email,
                "password": "directory-password",
            },
        )
    auth_app.dependency_overrides.clear()
    return response, db


@pytest.mark.parametrize("role", [UserRole.ADMIN, UserRole.MEMBER, UserRole.VIEWER])
def test_login_issues_fixed_identity_claims_for_each_role(role):
    organization, user = identity(role)
    response, db = login_with(organization, user)

    assert response.status_code == 200
    claims = jwt.decode(
        response.json()["access_token"],
        get_settings().secret_key,
        algorithms=["HS256"],
        issuer="sentinel-auth",
        audience="sentinel-cortex",
    )
    assert claims["sub"] == str(user.id)
    assert claims["tenant_id"] == str(organization.id)
    assert claims["role"] == role.value
    assert claims["is_superuser"] is False
    assert claims["iss"] == "sentinel-auth"
    assert claims["aud"] == "sentinel-cortex"
    assert isinstance(claims["iat"], int) and isinstance(claims["exp"], int)
    assert claims["exp"] - claims["iat"] == 600
    # The tenant RLS setting is applied before the user query.
    assert db.execute.await_count == 4


@pytest.mark.parametrize("inactive", ["user", "organization"])
def test_login_rejects_inactive_user_or_organization(inactive):
    organization, user = identity(
        active=inactive != "user", org_active=inactive != "organization"
    )
    response, _ = login_with(organization, user)
    assert response.status_code == 401


def test_me_returns_database_user_and_rejects_stale_token_role():
    organization, user = identity(UserRole.ADMIN)
    login_response, _ = login_with(organization, user)
    token = login_response.json()["access_token"]

    db = AsyncMock()
    db.execute.side_effect = [
        result(sorted(EXPECTED_ALEMBIC_HEADS)),
        result([]),
        result([user]),
    ]
    db.get.return_value = organization
    install_db_override(auth_app, db)
    me = TestClient(auth_app).get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    auth_app.dependency_overrides.clear()
    assert me.status_code == 200
    assert me.json()["id"] == str(user.id)

    stale_claims = {
        "sub": str(user.id),
        "tenant_id": str(user.organization_id),
        "role": UserRole.VIEWER.value,
        "is_superuser": False,
        "iss": "sentinel-auth",
        "aud": "sentinel-cortex",
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int(datetime.now(timezone.utc).timestamp()) + 600,
    }
    stale = jwt.encode(stale_claims, get_settings().secret_key, algorithm="HS256")
    db = AsyncMock()
    db.execute.side_effect = [
        result(sorted(EXPECTED_ALEMBIC_HEADS)),
        result([]),
        result([user]),
    ]
    db.get.return_value = organization
    install_db_override(auth_app, db)
    rejected = TestClient(auth_app).get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {stale}"}
    )
    auth_app.dependency_overrides.clear()
    assert rejected.status_code == 401


def test_member_cannot_create_users():
    member = User(
        id=uuid4(), organization_id=uuid4(), email="member@example.com",
        username="member", password_hash="unused", first_name="Member",
        last_name="User", role=UserRole.MEMBER, is_active=True, is_superuser=False,
    )
    app = FastAPI()
    app.include_router(users_router)
    app.dependency_overrides[get_current_user] = lambda: member
    app.dependency_overrides[get_db] = lambda: AsyncMock()

    response = TestClient(app).post(
        "/api/v1/users/",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "organization_id": str(member.organization_id),
        },
    )
    app.dependency_overrides.clear()
    assert response.status_code == 403


def test_auth_health_requires_current_alembic_heads():
    db = AsyncMock()
    db.execute.return_value = result(sorted(EXPECTED_ALEMBIC_HEADS))
    install_db_override(auth_app, db)
    healthy = TestClient(auth_app).get("/api/v1/auth/health")
    auth_app.dependency_overrides.clear()
    assert healthy.status_code == 200

    db = AsyncMock()
    db.execute.return_value = result(["4c53459a200b"])
    install_db_override(auth_app, db)
    outdated = TestClient(auth_app).get("/api/v1/auth/health")
    auth_app.dependency_overrides.clear()
    assert outdated.status_code == 503
