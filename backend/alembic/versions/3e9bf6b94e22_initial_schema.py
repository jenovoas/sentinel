"""initial schema

Revision ID: 3e9bf6b94e22
Revises: 
Create Date: 2025-12-13 20:45:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3e9bf6b94e22"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tenants
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # Audit logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource", sa.String(length=100), nullable=False),
        sa.Column("details", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    # Indexes
    op.create_index("idx_audit_logs_tenant_id", "audit_logs", ["tenant_id"], unique=False)
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)

    # Default seed data
    op.execute(
        """
        INSERT INTO tenants (id, name, slug, is_active)
        VALUES ('00000000-0000-0000-0000-000000000000', 'Default Tenant', 'default', true)
        ON CONFLICT (slug) DO NOTHING;
        """
    )

    # Row Level Security policies
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'users' AND policyname = 'rls_users_tenant'
            ) THEN
                EXECUTE 'CREATE POLICY rls_users_tenant ON public.users USING (tenant_id = current_setting(''app.current_tenant_id'')::uuid)';
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM pg_policies WHERE schemaname = 'public' AND tablename = 'audit_logs' AND policyname = 'rls_audit_logs_tenant'
            ) THEN
                EXECUTE 'CREATE POLICY rls_audit_logs_tenant ON public.audit_logs USING (tenant_id = current_setting(''app.current_tenant_id'')::uuid)';
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS rls_audit_logs_tenant ON public.audit_logs;")
    op.execute("DROP POLICY IF EXISTS rls_users_tenant ON public.users;")
    op.execute("ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY;")

    op.drop_index("idx_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("idx_audit_logs_tenant_id", table_name="audit_logs")

    op.drop_table("audit_logs")
    op.drop_table("users")
    op.drop_table("tenants")
