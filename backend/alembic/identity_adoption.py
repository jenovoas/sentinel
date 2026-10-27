"""Adopta únicamente el esquema exacto creado por el init.sql histórico."""

import re

from sqlalchemy import inspect, text


LEGACY_COLUMNS = {
    "tenants": {
        "id": ("VARCHAR", 36),
        "name": ("VARCHAR", 255),
        "slug": ("VARCHAR", 100),
        "is_active": ("BOOLEAN", None),
        "created_at": ("TIMESTAMP", None),
        "updated_at": ("TIMESTAMP", None),
    },
    "users": {
        "id": ("VARCHAR",36),
        "tenant_id": ("VARCHAR",36),
        "email": ("VARCHAR",255),
        "username": ("VARCHAR",100),
        "hashed_password": ("VARCHAR",255),
        "is_active": ("BOOLEAN", None),
        "is_superuser": ("BOOLEAN", None),
        "created_at": ("TIMESTAMP", None),
        "updated_at": ("TIMESTAMP", None),
    },
    "audit_logs": {
        "id": ("VARCHAR",36),
        "tenant_id": ("VARCHAR",36),
        "user_id": ("VARCHAR",36),
        "action": ("VARCHAR",100),
        "resource": ("VARCHAR",100),
        "details": ("TEXT", None),
        "ip_address": ("VARCHAR",45),
        "created_at": ("TIMESTAMP", None),
    },
}

def _fail(reason: str) -> RuntimeError:
    return RuntimeError(
        "No se puede adoptar el esquema de identidad sin una revisión manual: " + reason
    )


def _validate_legacy_schema(connection) -> None:
    inspector = inspect(connection)
    names = set(inspector.get_table_names(schema="public"))
    present = names.intersection(LEGACY_COLUMNS)
    if present != set(LEGACY_COLUMNS):
        raise _fail(f"se encontraron tablas de identidad parciales: {sorted(present)}")
    if "organizations" in names:
        raise _fail("ya existe public.organizations sin una versión Alembic")

    expected_nullable = {
        "tenants": {"is_active"},
        "users": {"is_active", "is_superuser"},
        "audit_logs": {"user_id", "details", "ip_address"},
    }
    expected_unique = {
        "tenants": {("name",), ("slug",)},
        "users": {("email", "tenant_id")},
        "audit_logs": set(),
    }
    expected_foreign_keys = {
        "tenants": set(),
        "users": {
            ("users_tenant_id_fkey", ("tenant_id",), "tenants", ("id",), "CASCADE")
        },
        "audit_logs": {
            ("audit_logs_tenant_id_fkey", ("tenant_id",), "tenants", ("id",), "CASCADE"),
            ("audit_logs_user_id_fkey", ("user_id",), "users", ("id",), "SET NULL"),
        },
    }

    for table, expected_columns in LEGACY_COLUMNS.items():
        actual = {
            column["name"]: (column["type"].__class__.__name__.upper(), getattr(column["type"], "length", None))
            for column in inspector.get_columns(table, schema="public")
        }
        if actual != expected_columns:
            raise _fail(f"public.{table} no coincide con las columnas/tipos del init.sql conocido")
        nullable = {
            column["name"]
            for column in inspector.get_columns(table, schema="public")
            if column["nullable"]
        }
        if nullable != expected_nullable[table]:
            raise _fail(f"public.{table} no coincide con la nulabilidad del init.sql conocido")

        primary_key = tuple((inspector.get_pk_constraint(table, schema="public").get("constrained_columns") or ()))
        if primary_key != ("id",):
            raise _fail(f"public.{table} no tiene la clave primaria esperada sobre id")

        unique_columns = {
            tuple(constraint.get("column_names") or ())
            for constraint in inspector.get_unique_constraints(table, schema="public")
        }
        if unique_columns != expected_unique[table]:
            raise _fail(f"public.{table} tiene restricciones UNIQUE desconocidas")

        foreign_keys = {
            (
                foreign_key.get("name"),
                tuple(foreign_key.get("constrained_columns") or ()),
                foreign_key.get("referred_table"),
                tuple(foreign_key.get("referred_columns") or ()),
                (foreign_key.get("options") or {}).get("ondelete", "").upper(),
            )
            for foreign_key in inspector.get_foreign_keys(table, schema="public")
        }
        if foreign_keys != expected_foreign_keys[table]:
            raise _fail(f"public.{table} tiene claves foráneas desconocidas")

    policies = connection.execute(
        text(
            "SELECT tablename, policyname, permissive, roles, cmd, qual, with_check "
            "FROM pg_policies WHERE schemaname = 'public' AND policyname IN "
            "('rls_users_tenant', 'rls_audit_logs_tenant')"
        )
    ).all()
    expected_policies = {
        ("users", "rls_users_tenant"),
        ("audit_logs", "rls_audit_logs_tenant"),
    }
    if {(row.tablename, row.policyname) for row in policies} != expected_policies:
        raise _fail("las políticas RLS no coinciden con las del init.sql conocido")
    for policy in policies:
        expression = "".join((policy.qual or "").lower().split()).replace("(", "").replace(")", "")
        if (
            policy.permissive != "PERMISSIVE"
            or set(policy.roles or ()) != {"public"}
            or policy.cmd != "ALL"
            or policy.with_check is not None
            or "tenant_id=" not in expression
            or "current_setting('app.current_tenant_id'" not in expression
            or re.search(r"\b(?:or|and)\b", policy.qual or "", re.IGNORECASE)
        ):
            raise _fail(f"la política {policy.policyname} contiene reglas no reconocidas")

    rls_tables = connection.execute(
        text(
            "SELECT relname, relrowsecurity FROM pg_class "
            "WHERE relnamespace = 'public'::regnamespace AND relname IN ('users', 'audit_logs')"
        )
    ).all()
    if {(row.relname, row.relrowsecurity) for row in rls_tables} != {
        ("users", True),
        ("audit_logs", True),
    }:
        raise _fail("RLS no está habilitado exactamente en users y audit_logs")

    for table, column in (
        ("tenants", "id"),
        ("users", "id"),
        ("users", "tenant_id"),
        ("audit_logs", "id"),
        ("audit_logs", "tenant_id"),
        ("audit_logs", "user_id"),
    ):
        invalid = connection.execute(
            text(
                f"SELECT 1 FROM public.{table} WHERE {column} !~* "
                "'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$' LIMIT 1"
            )
        ).first()
        if invalid:
            raise _fail(f"public.{table}.{column} contiene identificadores que no son UUID")

    invalid_user = connection.execute(
        text(
            "SELECT 1 FROM public.users WHERE is_active IS NULL "
            "OR is_superuser IS NULL OR length(username) > 64 LIMIT 1"
        )
    ).first()
    if invalid_user:
        raise _fail("users contiene roles booleanos nulos o usernames de más de 64 caracteres")

    for column in ("email", "username"):
        duplicate = connection.execute(
            text(
                f"SELECT 1 FROM public.users GROUP BY {column} "
                "HAVING count(*) > 1 LIMIT 1"
            )
        ).first()
        if duplicate:
            raise _fail(f"users.{column} no es único globalmente; no se modificaron los datos")


def adopt_legacy_identity_schema(connection) -> bool:
    """Normaliza el baseline conocido y lo marca como revisión inicial ya aplicada.

    La conexión debe estar dentro de la transacción que ejecutará Alembic; así,
    cualquier fallo posterior revierte también la adopción y su marca de versión.
    """
    inspector = inspect(connection)
    if inspector.has_table("alembic_version", schema="public"):
        return False

    names = set(inspector.get_table_names(schema="public"))
    views = set(inspector.get_view_names(schema="public"))
    if views:
        raise _fail(f"hay vistas sin historial Alembic: {sorted(views)}")
    identity_tables = names.intersection(LEGACY_COLUMNS)
    if not identity_tables:
        if names:
            raise _fail(f"hay tablas sin historial Alembic: {sorted(names)}")
        return False
    if identity_tables != set(LEGACY_COLUMNS):
        raise _fail(f"se encontraron tablas de identidad parciales: {sorted(identity_tables)}")
    if names != set(LEGACY_COLUMNS):
        raise _fail(f"hay tablas ajenas al baseline legacy: {sorted(names - set(LEGACY_COLUMNS))}")

    _validate_legacy_schema(connection)

    connection.exec_driver_sql("DROP POLICY rls_users_tenant ON public.users")
    connection.exec_driver_sql("DROP POLICY rls_audit_logs_tenant ON public.audit_logs")

    for table, constraint in (
        ("users", "users_tenant_id_fkey"),
        ("audit_logs", "audit_logs_tenant_id_fkey"),
        ("audit_logs", "audit_logs_user_id_fkey"),
    ):
        connection.exec_driver_sql(
            f"ALTER TABLE public.{table} DROP CONSTRAINT {constraint}"
        )

    for table, columns in {
        "tenants": ("id",),
        "users": ("id", "tenant_id"),
        "audit_logs": ("id", "tenant_id", "user_id"),
    }.items():
        for column in columns:
            connection.exec_driver_sql(
                f"ALTER TABLE public.{table} ALTER COLUMN {column} "
                f"TYPE uuid USING {column}::uuid"
            )

    connection.exec_driver_sql(
        "ALTER TABLE public.users ADD CONSTRAINT users_email_key UNIQUE (email)"
    )
    connection.exec_driver_sql(
        "ALTER TABLE public.users ADD CONSTRAINT users_username_key UNIQUE (username)"
    )
    connection.exec_driver_sql(
        "ALTER TABLE public.users ADD CONSTRAINT users_tenant_id_fkey "
        "FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE"
    )
    connection.exec_driver_sql(
        "ALTER TABLE public.audit_logs ADD CONSTRAINT audit_logs_tenant_id_fkey "
        "FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE"
    )
    connection.exec_driver_sql(
        "ALTER TABLE public.audit_logs ADD CONSTRAINT audit_logs_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL"
    )

    connection.exec_driver_sql(
        "CREATE POLICY rls_users_tenant ON public.users "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )
    connection.exec_driver_sql(
        "CREATE POLICY rls_audit_logs_tenant ON public.audit_logs "
        "USING (tenant_id = current_setting('app.current_tenant_id')::uuid)"
    )
    connection.exec_driver_sql(
        "INSERT INTO public.tenants (id, name, slug, is_active) "
        "VALUES ('00000000-0000-0000-0000-000000000000', 'Default Tenant', 'default', true) "
        "ON CONFLICT (slug) DO NOTHING"
    )
    connection.exec_driver_sql(
        "CREATE TABLE public.alembic_version (version_num varchar(32) NOT NULL PRIMARY KEY)"
    )
    connection.exec_driver_sql(
        "INSERT INTO public.alembic_version (version_num) VALUES ('3e9bf6b94e22')"
    )
    return True
