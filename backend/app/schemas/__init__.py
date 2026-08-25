# Autor: Jaime Novoa Sepúlveda — Todos los derechos reservados.
# Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
# Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .auth import Token, TokenData
from .users import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    User,
    UserWithOrganization,
)
from .users import (
    UserCreate as UserCreateNew,
)
from .users import (
    UserUpdate as UserUpdateNew,
)

__all__ = [
    "Token",
    "TokenData",
    "Organization",
    "OrganizationCreate",
    "OrganizationUpdate",
    "User",
    "UserWithOrganization",
    "UserCreateNew",
    "UserUpdateNew",
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "HealthResponse",
]


# Legacy Tenant Schemas (for backward compatibility)
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=100)


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=100)
    is_active: Optional[bool] = None


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Legacy User Schemas (for backward compatibility)
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)
    tenant_id: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_superuser: bool
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Health Check Schema
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: bool
    redis: bool
    celery: bool

