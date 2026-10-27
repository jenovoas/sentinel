# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import Token
from app.security.auth import (
    create_access_token,
    ensure_schema_current,
    set_tenant_context,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    organization_slug: str = Form(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    await ensure_schema_current(db)
    org_result = await db.execute(
        select(Organization).where(Organization.slug == organization_slug)
    )
    organization = org_result.scalars().first()
    if organization is None or not organization.is_active:
        raise _login_failed()

    await set_tenant_context(db, organization.id)
    user_result = await db.execute(
        select(User).where(
            User.email == form_data.username,
            User.organization_id == organization.id,
        )
    )
    user = user_result.scalars().first()
    if user is None or not user.is_active or not verify_password(form_data.password, user.password_hash):
        raise _login_failed()

    return {"access_token": create_access_token(user), "token_type": "bearer"}


def _login_failed() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect organization, email, or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
