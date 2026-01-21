"""
Sentinel User Model - Multi-tenant User with Organization relationship
SQLAlchemy 2.0 + PostgreSQL UUID support
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Role enum for user permissions
class UserRole(str, PyEnum):
    """User role permissions: admin > member > viewer"""
    ADMIN = "admin"      # Full access, org management
    MEMBER = "member"    # Backup operations, monitoring
    VIEWER = "viewer"    # Read-only access


class User(Base):
    __tablename__ = "users"

    # Primary key: UUID v4 (PostgreSQL native)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Foreign key to organization (multi-tenancy)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Profile fields
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)

    # Permissions
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum"),
        default=UserRole.MEMBER,
        nullable=False,
        index=True
    )

    # Legacy field for backward compatibility
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    # Audit fields (auto-managed)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="users",
        lazy="selectin"
    )

    # Legacy relationship property for backward compatibility
    @property
    def tenant(self):
        """Alias for organization (backward compatibility)"""
        return self.organization

    def __repr__(self) -> str:
        """Debug representation"""
        return (f"<User(id='{self.id}', email='{self.email}', "
                f"organization_id='{self.organization_id}', "
                f"role='{self.role}', is_active={self.is_active})>")

    def __str__(self) -> str:
        """Human readable"""
        return f"{self.first_name} {self.last_name} (@{self.username})"

    @property
    def full_name(self) -> str:
        """Convenience property"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self) -> bool:
        """Quick admin check"""
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_member(self) -> bool:
        """Quick member check"""
        return self.role in (UserRole.ADMIN, UserRole.MEMBER)

    def activate(self) -> None:
        """Activate user account"""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate user account"""
        self.is_active = False
