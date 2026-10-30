from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import Token
from app.security.auth import (
    create_access_token,
    ensure_schema_current,
    get_current_user,
    set_tenant_context,
)
from app.services.directory_auth import DirectoryUnavailable, authenticate_directory_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    organization_slug: str = Form(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_db),
):
    await ensure_schema_current(db)
    organization_result = await db.execute(
        select(Organization).where(Organization.slug == organization_slug)
    )
    organization = organization_result.scalars().first()
    if organization is None or not organization.is_active:
        raise _login_failed()

    try:
        directory_user = await authenticate_directory_user(
            form_data.username, form_data.password
        )
    except DirectoryUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Directory authentication is temporarily unavailable",
        ) from None
    if directory_user is None:
        raise _login_failed()

    await set_tenant_context(db, organization.id)
    user_result = await db.execute(
        select(User).where(
            User.organization_id == organization.id,
            User.directory_id == directory_user.directory_id,
        )
    )
    user = user_result.scalars().first()

    if user is None:
        email_key = directory_user.email.casefold()
        user_result = await db.execute(
            select(User).where(
                User.organization_id == organization.id,
                func.lower(User.email) == email_key,
            )
        )
        user = user_result.scalars().first()
        if user is not None and user.directory_id not in (None, directory_user.directory_id):
            user = None

    if user is None or not user.is_active:
        raise _login_failed()

    # The database row is a tenant authorization/profile mapping, not a
    # credential store. Bind it once to AD's immutable objectGUID.
    user.directory_id = directory_user.directory_id
    user.email = directory_user.email
    user.is_superuser = directory_user.is_sentinel_admin
    await db.commit()

    return {"access_token": create_access_token(user), "token_type": "bearer"}


def _login_failed() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect organization, email, or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me")
async def current_identity(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "organization_id": str(current_user.organization_id),
        "role": current_user.role.value,
        "is_superuser": current_user.is_superuser,
    }
