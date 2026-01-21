from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.schemas import TenantCreate, TenantUpdate

def get_tenant(db: Session, tenant_id: int):
    return db.query(Tenant).filter(Tenant.id == tenant_id).first()

def get_tenant_by_slug(db: Session, slug: str):
    return db.query(Tenant).filter(Tenant.slug == slug).first()

def get_tenants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tenant).offset(skip).limit(limit).all()

def create_tenant(db: Session, tenant: TenantCreate):
    db_tenant = Tenant(**tenant.dict())
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant
