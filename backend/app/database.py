"""
Async Database Configuration for Sentinel Application.

SQLAlchemy 2.0 with async/await support using asyncpg driver (3-5x faster).
"""

from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config import get_settings

settings = get_settings()

# Convert DATABASE_URL to async format
DATABASE_URL = settings.database_url
if not DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# ============================================================================
# DATABASE ENGINE
# ============================================================================

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
    connect_args={
        "server_settings": {
            "application_name": "sentinel_api",
            "jit": "off",
        },
        "timeout": 10,
    },
)

# ============================================================================
# SESSION FACTORY
# ============================================================================

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ============================================================================
# ORM BASE CLASS
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    __abstract__ = True


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database sessions.
    
    Example:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# CONTEXT MANAGER
# ============================================================================

class AsyncDatabaseSession:
    """Context manager for async database sessions in non-HTTP code."""

    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> AsyncSession:
        """Enter async context."""
        self.session = AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context."""
        if self.session:
            try:
                if exc_type is None:
                    await self.session.commit()
                else:
                    await self.session.rollback()
            finally:
                await self.session.close()


# ============================================================================
# INITIALIZATION
# ============================================================================

async def init_db() -> None:
    """Initialize database on application startup."""
    try:
        # Enable extensions
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
                await session.commit()
            except Exception:
                await session.rollback()
        
        # Create all tables from models
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database initialized successfully")
        print(f"   Driver: asyncpg")
        print(f"   Pool: NullPool (Docker-ready)")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


# ============================================================================
# CLEANUP
# ============================================================================

async def close_db() -> None:
    """Close database on shutdown."""
    await engine.dispose()
    print("✅ Database connections closed")


# ============================================================================
# HEALTH CHECKS
# ============================================================================

async def health_check() -> dict:
    """Health check for monitoring."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "db_connection": True,
            "async_driver": "asyncpg",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "db_connection": False,
            "async_driver": "asyncpg",
            "error": str(e),
        }


async def check_db_connection() -> dict:
    """Simple database connection check."""
    try:
        result = await health_check()
        return result
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


async def test_connection() -> bool:
    """Direct connection test used by CLI helpers."""
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True


__all__ = [
    "engine",
    "AsyncSessionLocal",
    "Base",
    "get_db",
    "AsyncDatabaseSession",
    "init_db",
    "close_db",
    "health_check",
    "check_db_connection",
    "test_connection",
]
