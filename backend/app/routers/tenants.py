"""
Tenants router for Sentinel application.

This router handles all tenant-related endpoints, including:
- Tenant creation
- Tenant listing
- Tenant retrieval
- Tenant updates
- Tenant deletion
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas import TenantCreate, TenantUpdate, TenantResponse
from app.services.tenant_service import (
    create_tenant as create_tenant_service,
    get_tenants,
    get_tenant as get_tenant_service,
)
from app.auth_utils import get_current_user
from typing import List

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
def create_tenant(tenant: TenantCreate, db: Session = Depends(get_db)):
    """
    Creates a new tenant.

    This is a public endpoint that allows new tenants to be created.
    """
    return create_tenant_service(db=db, tenant=tenant)

@router.get("/", response_model=List[TenantResponse])
def list_tenants(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists all tenants.

    This is a protected endpoint that requires authentication.
    It returns a list of all tenants. In a real-world application, this
    should be restricted to superusers.
    """
    tenants = get_tenants(db, skip=skip, limit=limit)
    return tenants

@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Gets a specific tenant.

    This is a protected endpoint that requires authentication.
    It returns the tenant with the specified ID. In a real-world application,
    this should be restricted to superusers or users of that tenant.
    """
    tenant = get_tenant_service(db, tenant_id=tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: str,
    tenant: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Updates a tenant.

    This is a protected endpoint that requires authentication.
    It updates the tenant with the specified ID. In a real-world application,
    this should be restricted to superusers or users of that tenant.
    """
    db_tenant = get_tenant_service(db, tenant_id=tenant_id)
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    update_data = tenant.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_tenant, field, value)
    
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a tenant.

    This is a protected endpoint that requires authentication.
    It deletes the tenant with the specified ID. In a real-world application,
    this should be restricted to superusers.
    """
    db_tenant = get_tenant_service(db, tenant_id=tenant_id)
    if not db_tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    db.delete(db_tenant)
    db.commit()
    return None
