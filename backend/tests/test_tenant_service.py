# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.tenant import Tenant
from app.schemas import TenantCreate
from app.services.tenant_service import create_tenant, get_tenant, get_tenant_by_slug, get_tenants


@pytest.mark.asyncio
async def test_create_tenant():
    db = AsyncMock()
    tenant_data = TenantCreate(name="Test Tenant", slug="test-tenant")

    # We don't need to mock return value of add, but we need to ensure refresh works if we use it
    # However, since we are using a mock, we can just check if it was called.

    result = await create_tenant(db, tenant_data)

    assert result.name == "Test Tenant"
    assert result.slug == "test-tenant"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_get_tenant():
    db = AsyncMock()
    tenant_id = str(uuid4())
    mock_tenant = Tenant(id=tenant_id, name="Test Tenant", slug="test-tenant")

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_tenant
    db.execute.return_value = mock_result

    result = await get_tenant(db, tenant_id)

    assert result == mock_tenant
    db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_tenant_by_slug():
    db = AsyncMock()
    slug = "test-tenant"
    mock_tenant = Tenant(id=uuid4(), name="Test Tenant", slug=slug)

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_tenant
    db.execute.return_value = mock_result

    result = await get_tenant_by_slug(db, slug)

    assert result == mock_tenant
    db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_tenants():
    db = AsyncMock()
    mock_tenants = [
        Tenant(id=uuid4(), name="T1", slug="t1"),
        Tenant(id=uuid4(), name="T2", slug="t2")
    ]

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_tenants
    db.execute.return_value = mock_result

    result = await get_tenants(db, skip=0, limit=10)

    assert len(result) == 2
    assert result == mock_tenants
    db.execute.assert_called_once()
