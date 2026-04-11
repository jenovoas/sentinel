import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import jwt
from fastapi import HTTPException, status
from app.security.auth import get_current_user, get_current_user_model
from app.config import get_settings
from app.schemas.auth import TokenData
from app.models.user import User

settings = get_settings()

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    # Setup
    username = "testuser"
    payload = {"sub": username, "exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    # Execute
    token_data = await get_current_user(token=token)

    # Verify
    assert isinstance(token_data, TokenData)
    assert token_data.username == username

@pytest.mark.asyncio
async def test_get_current_user_missing_sub():
    # Setup
    payload = {"exp": datetime.utcnow() + timedelta(minutes=30)}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    # Execute & Verify
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    # Setup
    token = "invalid.token.string"

    # Execute & Verify
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    # Setup
    username = "testuser"
    payload = {"sub": username, "exp": datetime.utcnow() - timedelta(minutes=30)}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    # Execute & Verify
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_model_success():
    # Setup
    username = "testuser"
    token_data = TokenData(username=username)
    db = AsyncMock()

    mock_user = User(username=username)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_user
    db.execute.return_value = mock_result

    # Execute
    user = await get_current_user_model(token_data=token_data, db=db)

    # Verify
    assert user == mock_user
    db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_current_user_model_not_found():
    # Setup
    username = "nonexistent"
    token_data = TokenData(username=username)
    db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    db.execute.return_value = mock_result

    # Execute & Verify
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user_model(token_data=token_data, db=db)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "User not found"
