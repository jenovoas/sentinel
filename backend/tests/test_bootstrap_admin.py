from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.bootstrap_admin import BootstrapError, provision_initial_superuser
from app.models.organization import Organization
from app.models.user import UserRole
from app.security.auth import EXPECTED_ALEMBIC_HEADS, verify_password


def scalars(rows):
    mock = MagicMock()
    mock.scalars.return_value.all.return_value = rows
    mock.scalars.return_value.first.return_value = rows[0] if rows else None
    return mock


def version_result(heads=EXPECTED_ALEMBIC_HEADS):
    return scalars(list(heads))


def bootstrap_inputs(**overrides):
    return {
        "organization_slug": "acme",
        "email": "owner@example.com",
        "username": "owner",
        "first_name": "Initial",
        "last_name": "Owner",
        "password": "safe-password-123",
        "password_confirmation": "safe-password-123",
        **overrides,
    }


@pytest.mark.asyncio
async def test_bootstrap_aborts_if_any_superuser_exists():
    db = AsyncMock()
    db.add = MagicMock()
    existing = MagicMock()
    existing.scalar_one_or_none.return_value = uuid4()
    db.execute.side_effect = [
        version_result(),
        MagicMock(),  # row_security = off
        MagicMock(),  # transaction advisory lock
        existing,
    ]

    with pytest.raises(BootstrapError, match="Ya existe un superusuario"):
        await provision_initial_superuser(db, **bootstrap_inputs())

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_bootstrap_creates_admin_superuser_for_active_organization():
    organization = Organization(
        id=uuid4(), name="Acme", slug="acme", is_active=True
    )
    db = AsyncMock()
    db.add = MagicMock()
    no_superuser = MagicMock()
    no_superuser.scalar_one_or_none.return_value = None
    tenant_result = MagicMock()
    tenant_result.scalar_one_or_none.return_value = organization.id
    db.execute.side_effect = [
        version_result(),
        MagicMock(),  # row_security = off
        MagicMock(),  # transaction advisory lock
        no_superuser,
        scalars([organization]),
        tenant_result,
        MagicMock(),  # transaction-local tenant context
    ]

    user = await provision_initial_superuser(db, **bootstrap_inputs())

    assert user.organization_id == organization.id
    assert user.tenant_id == organization.id
    assert user.role is UserRole.ADMIN
    assert user.is_superuser is True
    assert user.is_active is True
    assert verify_password("safe-password-123", user.password_hash)
    db.add.assert_called_once_with(user)
    db.commit.assert_awaited_once()
    db.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_bootstrap_rejects_schema_not_at_exact_head():
    db = AsyncMock()
    db.add = MagicMock()
    db.execute.return_value = scalars(["old_revision"])

    with pytest.raises(HTTPException) as error:
        await provision_initial_superuser(db, **bootstrap_inputs())

    assert error.value.status_code == 503
    db.add.assert_not_called()
    db.commit.assert_not_awaited()
    db.rollback.assert_awaited_once()
