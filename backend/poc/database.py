"""
Sentinel Vault - Database Models
SQLAlchemy models for PostgreSQL
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Document(Base):
    """Document metadata (encrypted files)"""
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, nullable=False)  # User who owns this document
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Path to encrypted file
    file_hash = Column(String, nullable=False)  # SHA-256 hash
    file_size = Column(Integer, nullable=False)  # Bytes
    category = Column(String, default='general')
    tags = Column(JSON, default=[])  # List of tags
    nonce = Column(String, nullable=False)  # For decryption
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)


class Wallet(Base):
    """Crypto wallet metadata"""
    __tablename__ = 'wallets'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    chain = Column(String, nullable=False)  # bitcoin, ethereum, etc.
    address = Column(String, nullable=False)
    encrypted_seed = Column(String)  # Encrypted seed phrase
    nonce = Column(String)  # For decryption
    created_at = Column(DateTime, default=datetime.utcnow)


class Password(Base):
    """Password vault entries"""
    __tablename__ = 'passwords'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    service = Column(String, nullable=False)
    username = Column(String)
    encrypted_password = Column(String, nullable=False)
    nonce = Column(String, nullable=False)
    url = Column(String)
    notes = Column(String)
    category = Column(String, default='general')
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Note(Base):
    """Encrypted notes (Obsidian-style)"""
    __tablename__ = 'notes'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    encrypted_content = Column(String, nullable=False)  # Ciphertext
    nonce = Column(String, nullable=False)  # For decryption
    content_length = Column(Integer, default=0)  # Original length
    links = Column(JSON, default=[])  # [[Note Name]] links
    tags = Column(JSON, default=[])  # #tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime, default=datetime.utcnow)


# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./sentinel_vault.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database (create tables)"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("🗄️  Initializing Sentinel Vault Database\n")
    init_db()
    
    # Test connection
    db = SessionLocal()
    print(f"✅ Database connection successful")
    print(f"   URL: {DATABASE_URL}")
    print(f"   Tables: {Base.metadata.tables.keys()}")
    db.close()
