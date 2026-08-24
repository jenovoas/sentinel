# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tenant import Tenant
from app.schemas import TenantCreate

async def get_tenant(db: AsyncSession, tenant_id: str):
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalars().first()

async def get_tenant_by_slug(db: AsyncSession, slug: str):
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    return result.scalars().first()

async def get_tenants(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Tenant).offset(skip).limit(limit))
    return result.scalars().all()

async def create_tenant(db: AsyncSession, tenant: TenantCreate):
    db_tenant = Tenant(**tenant.model_dump())
    db.add(db_tenant)
    await db.commit()
    await db.refresh(db_tenant)
    return db_tenant
