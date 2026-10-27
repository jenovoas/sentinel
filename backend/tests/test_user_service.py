# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.user import User
from app.schemas import UserCreate
from app.services.user_service import create_user, get_user, get_user_by_email


@pytest.mark.asyncio
async def test_get_user():
    db = AsyncMock()
    user_id = str(uuid4())
    mock_user = User(id=user_id, email="test@example.com", username="testuser")

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    db.execute.return_value = mock_result

    result = await get_user(db, user_id)

    assert result == mock_user
    db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_by_email():
    db = AsyncMock()
    email = "test@example.com"
    mock_user = User(id=uuid4(), email=email, username="testuser")

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    db.execute.return_value = mock_result

    result = await get_user_by_email(db, email)

    assert result == mock_user
    db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_persists_both_tenant_and_organization_ids():
    organization_id = uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    data = UserCreate(
        email="member@example.com",
        username="member",
        password="secure-password",
        tenant_id=str(organization_id),
    )

    created = await create_user(db, data)

    assert created.organization_id == organization_id
    assert created.tenant_id == organization_id
    db.add.assert_called_once_with(created)
    db.commit.assert_awaited_once()
