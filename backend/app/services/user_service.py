"""
User service - Business logic for user operations
Supports both legacy (tenant_id) and new (organization_id) schemas
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas import UserCreate
from app.security import get_password_hash, verify_password
from app.services.tenant_service import get_tenant_by_slug


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    """
    Create a new user. Supports both legacy tenant_id and new organization_id.
    """
    hashed_password = get_password_hash(user.password)
    
    # Determine organization/tenant ID
    org_id = getattr(user, 'organization_id', None) or user.tenant_id
    if not org_id:
        default_tenant = get_tenant_by_slug(db, "default")
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
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user
