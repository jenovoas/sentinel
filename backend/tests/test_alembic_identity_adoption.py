"""Pruebas de adopción de esquema.

Prueba PostgreSQL optativa, solo en una base desechable vacía:
SENTINEL_MIGRATION_TEST_URL=postgresql://.../sentinel_migration_test \
    pytest -q tests/test_alembic_identity_adoption.py
La prueba de integración abre una transacción y la revierte; no se conecta a
ninguna base salvo que la URL termine exactamente en sentinel_migration_test.
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND / "alembic"))
from identity_adoption import adopt_legacy_identity_schema  # noqa: E402


class FakeInspector:
    def __init__(self, tables=(), has_version=False):
        self.tables = list(tables)
        self.has_version = has_version

    def has_table(self, name, schema=None):
        assert schema == "public"
        return name == "alembic_version" and self.has_version

    def get_table_names(self, schema=None):
        assert schema == "public"
        return self.tables

    def get_view_names(self, schema=None):
        assert schema == "public"
        return []


def test_clean_database_does_not_adopt(monkeypatch):
    monkeypatch.setattr("identity_adoption.inspect", lambda _connection: FakeInspector())
    assert adopt_legacy_identity_schema(object()) is False


def test_existing_alembic_history_is_never_rewritten(monkeypatch):
    monkeypatch.setattr(
        "identity_adoption.inspect",
        lambda _connection: FakeInspector(("users",), has_version=True),
    )
    assert adopt_legacy_identity_schema(object()) is False


def test_partial_unversioned_schema_is_rejected_without_ddl(monkeypatch):
    monkeypatch.setattr(
        "identity_adoption.inspect", lambda _connection: FakeInspector(("users",))
    )
    with pytest.raises(RuntimeError, match="tablas de identidad parciales"):
        adopt_legacy_identity_schema(object())


def test_unknown_unversioned_tables_are_rejected(monkeypatch):
    monkeypatch.setattr(
        "identity_adoption.inspect", lambda _connection: FakeInspector(("other_table",))
    )
    with pytest.raises(RuntimeError, match="tablas sin historial Alembic"):
        adopt_legacy_identity_schema(object())


def test_migration_graph_has_one_head():
    config = Config(str(BACKEND / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    assert len(ScriptDirectory.from_config(config).get_heads()) == 1


def test_postgres_adopts_only_an_empty_opt_in_test_database():
    database_url = os.getenv("SENTINEL_MIGRATION_TEST_URL")
    if not database_url:
        pytest.skip("define SENTINEL_MIGRATION_TEST_URL para PostgreSQL optativo")
    if urlparse(database_url).path.lstrip("/") != "sentinel_migration_test":
        pytest.fail("la URL debe apuntar exactamente a sentinel_migration_test")

    from sqlalchemy import create_engine, inspect, text

    engine = create_engine(database_url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            inspector = inspect(connection)
            if inspector.get_table_names(schema="public"):
                pytest.fail("el esquema public de la base optativa debe estar vacío")

            connection.exec_driver_sql(
                "CREATE TABLE public.tenants ("
                "id VARCHAR(36) PRIMARY KEY, name VARCHAR(255) NOT NULL UNIQUE, "
                "slug VARCHAR(100) NOT NULL UNIQUE, is_active BOOLEAN DEFAULT true, "
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                "CONSTRAINT unique_tenant_slug UNIQUE (slug))"
            )
            connection.exec_driver_sql(
                "CREATE TABLE public.users ("
                "id VARCHAR(36) PRIMARY KEY, tenant_id VARCHAR(36) NOT NULL "
                "REFERENCES public.tenants(id) ON DELETE CASCADE, email VARCHAR(255) NOT NULL, "
                "username VARCHAR(100) NOT NULL, hashed_password VARCHAR(255) NOT NULL, "
                "is_active BOOLEAN DEFAULT true, is_superuser BOOLEAN DEFAULT false, "
                "created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                "updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, "
                "CONSTRAINT unique_user_email_tenant UNIQUE (email, tenant_id))"
            )
            connection.exec_driver_sql(
                "CREATE TABLE public.audit_logs ("
                "id VARCHAR(36) PRIMARY KEY, tenant_id VARCHAR(36) NOT NULL "
                "REFERENCES public.tenants(id) ON DELETE CASCADE, "
                "user_id VARCHAR(36) REFERENCES public.users(id) ON DELETE SET NULL, "
                "action VARCHAR(100) NOT NULL, resource VARCHAR(100) NOT NULL, details TEXT, "
                "ip_address VARCHAR(45), created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )
            connection.exec_driver_sql("ALTER TABLE public.users ENABLE ROW LEVEL SECURITY")
            connection.exec_driver_sql("ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY")
            connection.exec_driver_sql(
                "CREATE POLICY rls_users_tenant ON public.users USING "
                "(tenant_id = current_setting('app.current_tenant_id')::varchar(36))"
            )
            connection.exec_driver_sql(
                "CREATE POLICY rls_audit_logs_tenant ON public.audit_logs USING "
                "(tenant_id = current_setting('app.current_tenant_id')::varchar(36))"
            )
            connection.exec_driver_sql(
                "INSERT INTO public.tenants (id, name, slug) VALUES "
                "('00000000-0000-0000-0000-000000000001', 'Tenant', 'tenant')"
            )
            connection.exec_driver_sql(
                "INSERT INTO public.users (id, tenant_id, email, username, hashed_password) "
                "VALUES ('00000000-0000-0000-0000-000000000002', "
                "'00000000-0000-0000-0000-000000000001', 'test@example.invalid', 'tester', 'hash')"
            )

            assert adopt_legacy_identity_schema(connection) is True
            assert connection.execute(
                text("SELECT version_num FROM public.alembic_version")
            ).scalar_one() == "3e9bf6b94e22"
            assert "UUID" in str(inspect(connection).get_columns("users", schema="public")[0]["type"]).upper()
            assert connection.execute(
                text("SELECT id FROM public.users")
            ).scalar_one() == "00000000-0000-0000-0000-000000000002"
        finally:
            transaction.rollback()
            engine.dispose()
