"""Offline, one-time bootstrap for the first organization superuser."""

import asyncio
import sys

from pydantic import ValidationError
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.organization import Organization
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.users import UserCreate as UserCreateSchema
from app.security.auth import ensure_schema_current, set_tenant_context


class BootstrapError(RuntimeError):
    pass


async def provision_initial_superuser(
    db: AsyncSession,
    *,
    organization_slug: str,
    email: str,
    username: str,
    first_name: str,
    last_name: str,
) -> User:
    """Create a tenant mapping; AD remains the only credential authority."""
    try:
        await ensure_schema_current(db)
        # The global check must not be silently narrowed by RLS; insufficient DB
        # privileges raise and abort instead of allowing a duplicate bootstrap.
        await db.execute(text("SET LOCAL row_security = off"))
        await db.execute(text("SELECT pg_advisory_xact_lock(hashtext('sentinel.bootstrap_admin'))"))
        existing = await db.execute(
            select(User.id).where(User.is_superuser.is_(True)).limit(1)
        )
        if existing.scalar_one_or_none() is not None:
            raise BootstrapError("Ya existe un superusuario; se cancela el aprovisionamiento")

        result = await db.execute(
            select(Organization).where(
                Organization.slug == organization_slug,
                Organization.is_active.is_(True),
            )
        )
        organization = result.scalars().first()
        if organization is None:
            raise BootstrapError("La organización no existe o está inactiva")
        tenant_result = await db.execute(
            select(Tenant.id).where(
                Tenant.id == organization.id,
                Tenant.is_active.is_(True),
            )
        )
        if tenant_result.scalar_one_or_none() is None:
            raise BootstrapError("No existe el tenant activo con el mismo UUID de la organización")

        account = UserCreateSchema(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            organization_id=organization.id,
            role=UserRole.ADMIN,
        )
        await set_tenant_context(db, organization.id)
        user = User(
            email=str(account.email),
            username=account.username,
            first_name=account.first_name,
            last_name=account.last_name,
            directory_id=None,
            password_hash=None,
            organization_id=organization.id,
            tenant_id=organization.id,
            role=UserRole.ADMIN,
            is_superuser=True,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        return user
    except Exception:
        await db.rollback()
        raise


async def _run(values: dict[str, str]) -> int:
    try:
        async with AsyncSessionLocal() as db:
            user = await provision_initial_superuser(db, **values)
        print(f"Superusuario creado para {values['organization_slug']}: {user.email}")
        return 0
    except (BootstrapError, ValidationError):
        print("No se pudo crear el superusuario; revise los datos y el estado de la DB.", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"No se pudo crear el superusuario ({type(exc).__name__}).", file=sys.stderr)
        return 1


def main() -> None:
    values = {
        "organization_slug": input("Slug de organización: ").strip(),
        "email": input("Email: ").strip(),
        "username": input("Username: ").strip(),
        "first_name": input("Nombre: ").strip(),
        "last_name": input("Apellido: ").strip(),
    }
    raise SystemExit(asyncio.run(_run(values)))


if __name__ == "__main__":
    main()
