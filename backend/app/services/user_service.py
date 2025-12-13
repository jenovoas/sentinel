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
    hashed_password = get_password_hash(user.password)
    
    tenant_id = user.tenant_id
    if not tenant_id:
        default_tenant = get_tenant_by_slug(db, "default")
        if not default_tenant:
            # This is a critical problem, the default tenant should always exist
            raise Exception("Default tenant not found")
        tenant_id = default_tenant.id

    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        tenant_id=tenant_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
