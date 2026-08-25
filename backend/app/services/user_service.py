# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
User service - Business logic for user operations
Supports both legacy (tenant_id) and new (organization_id) schemas
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas import UserCreate
from app.security import get_password_hash, verify_password
from app.services.tenant_service import get_tenant_by_slug


async def get_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: UserCreate):
    """
    Create a new user. Supports both legacy tenant_id and new organization_id.
    """
    hashed_password = get_password_hash(user.password)

    # Determine organization/tenant ID
    org_id = getattr(user, 'organization_id', None) or getattr(user, 'tenant_id', None)
    if not org_id:
        default_tenant = await get_tenant_by_slug(db, "default")
        if not default_tenant:
            raise Exception("Default tenant/organization not found")
        org_id = default_tenant.id

    # Create user with new model structure
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password,
        organization_id=org_id,
        first_name=getattr(user, 'first_name', 'User'),
        last_name=getattr(user, 'last_name', 'Account'),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """Authenticate user with email and password"""
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user
