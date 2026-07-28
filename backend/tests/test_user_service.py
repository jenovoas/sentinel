# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from app.services.user_service import get_user, get_user_by_email
from app.models.user import User

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
