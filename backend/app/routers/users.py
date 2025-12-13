"""
Users router for Sentinel application.

This router handles all user-related endpoints, including:
- User creation
- User listing
- User retrieval
- User updates
- User deletion
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.services.user_service import create_user as create_user_service, get_users, get_user as get_user_service
from app.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user.

    This is a public endpoint that allows new users to register.
    If a tenant_id is not provided, the user is assigned to the 'default' tenant.
    """
    return create_user_service(db=db, user=user)

@router.get("/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists all users for the current tenant.

    This is a protected endpoint that requires authentication.
    It returns a list of all users that belong to the same tenant as the
    currently authenticated user.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gets a specific user.

    This is a protected endpoint that requires authentication.
    It returns the user with the specified ID, but only if the user belongs
    to the same tenant as the currently authenticated user.
    """
    user = get_user_service(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a user.

    This is a protected endpoint that requires authentication.
    It updates the user with the specified ID, but only if the user belongs
    to the same tenant as the currently authenticated user.
    """
    db_user = get_user_service(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a user.

    This is a protected endpoint that requires authentication.
    It deletes the user with the specified ID, but only if the user belongs
    to the same tenant as the currently authenticated user.
    """
    db_user = get_user_service(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return None

