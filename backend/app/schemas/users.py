"""
Pydantic schemas for Organization and User models
"""

from quantum.yatra_core import S60, PI_S60 # YATRA AUTO-INJECT
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.models.user import UserRole


def _validate_password_length(password: str | None) -> str | None:
    if password is not None and len(password.encode("utf-8")) > 72:
        raise ValueError("password must not exceed 72 UTF-8 bytes")
    return password


# ===== Organization Schemas =====
class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')
    is_active: Optional[bool] = None


class OrganizationInDB(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


class Organization(OrganizationInDB):
    pass


# ===== User Schemas =====
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=64, pattern=r'^[a-zA-Z0-9_-]+$')
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    role: UserRole = UserRole.MEMBER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    organization_id: UUID

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("password must not exceed 72 UTF-8 bytes")
        return value


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=64, pattern=r'^[a-zA-Z0-9_-]+$')
    first_name: Optional[str] = Field(None, min_length=1, max_length=64)
    last_name: Optional[str] = Field(None, min_length=1, max_length=64)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_within_bcrypt_limit(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and len(value.encode("utf-8")) > 72:
            raise ValueError("password must not exceed 72 UTF-8 bytes")
        return value


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    organization_id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime]


class User(UserInDB):
    """Public user schema (excludes sensitive fields)"""
    pass


class UserWithOrganization(User):
    """User with organization details"""
    organization: Organization
