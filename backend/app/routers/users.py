# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
"""
Users router for Sentinel application.

This router handles all user-related endpoints, including:
- User creation
- User listing
- User retrieval
- User updates
- User deletion
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.security import get_current_admin_user, get_current_user
from app.services.user_service import create_user as create_user_service
from app.services.user_service import get_user as get_user_service

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Creates a new user.

    Requires authentication.
    If a tenant_id is not provided, the user is assigned to the 'default' tenant.
    """
    if (
        not current_user.is_superuser
        and user.organization_id != current_user.organization_id
    ):
        raise HTTPException(status_code=403, detail="Cannot create users outside your organization")
    return await create_user_service(db=db, user=user)

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists all users for the current tenant.

    This is a protected endpoint that requires authentication.
    It returns a list of all users that belong to the same tenant as the
    currently authenticated user.
    """
    query = select(User)
    if not current_user.is_superuser:
        query = query.where(User.organization_id == current_user.organization_id)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gets a specific user.

    This is a protected endpoint that requires authentication.
    It returns the user with the specified ID, but only if the user belongs
    to the same tenant as the currently authenticated user.
    """
    user = await get_user_service(db, user_id=user_id)
    if not user or (not current_user.is_superuser and user.organization_id != current_user.organization_id):
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a user.

    This is a protected endpoint that requires authentication.
    It updates the user with the specified ID, but only if the user belongs
    to the same tenant as the currently authenticated user.
    """
    db_user = await get_user_service(db, user_id=user_id)
    if not db_user or (not current_user.is_superuser and db_user.organization_id != current_user.organization_id):
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.model_dump(exclude_unset=True)
    if "is_active" in update_data and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin role required to change user privileges")
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Deletes a user.

    This is a protected endpoint that requires authentication.
    It deletes the user with the specified ID, but only if the user belongs
    to the same tenant as the currently authenticated user.
    """
    db_user = await get_user_service(db, user_id=user_id)
    if not db_user or (not current_user.is_superuser and db_user.organization_id != current_user.organization_id):
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(db_user)
    await db.commit()
    return None
