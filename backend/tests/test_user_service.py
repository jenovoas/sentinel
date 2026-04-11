import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.services.user_service import get_user, get_user_by_email, create_user
from app.models.user import User
from app.schemas import UserCreate
from app.schemas.users import UserCreate as UserCreateNew
from app.models.tenant import Tenant

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
async def test_create_user_with_tenant_id():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    tenant_id = str(uuid4())
    user_data = UserCreate(
        email="new@example.com",
        username="newuser",
        password="password123",
        tenant_id=tenant_id
    )

    with patch("app.services.user_service.get_password_hash", return_value="hashed_password"):
        result = await create_user(db, user_data)

    assert result.email == "new@example.com"
    assert result.username == "newuser"
    assert result.password_hash == "hashed_password"
    assert str(result.organization_id) == tenant_id
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_with_org_id():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    org_id = uuid4()
    user_data = UserCreateNew(
        email="org@example.com",
        username="orguser",
        first_name="Org",
        last_name="User",
        password="password123",
        organization_id=org_id
    )

    with patch("app.services.user_service.get_password_hash", return_value="hashed_password"):
        result = await create_user(db, user_data)

    assert result.organization_id == org_id
    db.add.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_default_fallback():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    default_tenant_id = uuid4()
    mock_tenant = MagicMock(spec=Tenant)
    mock_tenant.id = default_tenant_id

    user_data = UserCreate(
        email="default@example.com",
        username="defaultuser",
        password="password123"
    )

    with patch("app.services.user_service.get_password_hash", return_value="hashed_password"),          patch("app.services.user_service.get_tenant_by_slug", return_value=mock_tenant):
        result = await create_user(db, user_data)

    assert result.organization_id == default_tenant_id
    db.add.assert_called_once()

@pytest.mark.asyncio
async def test_create_user_no_default_fail():
    db = AsyncMock()
    user_data = UserCreate(
        email="fail@example.com",
        username="failuser",
        password="password123"
    )

    with patch("app.services.user_service.get_password_hash", return_value="hashed_password"),          patch("app.services.user_service.get_tenant_by_slug", return_value=None):
        with pytest.raises(Exception) as excinfo:
            await create_user(db, user_data)
        assert "Default tenant/organization not found" in str(excinfo.value)
