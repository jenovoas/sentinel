"""Add Organization model and User roles

Revision ID: 4c53459a200b
Revises: 3e9bf6b94e22
Create Date: 2025-12-13 23:22:42.700553

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4c53459a200b'
down_revision = '3e9bf6b94e22'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_role_enum
    op.execute("CREATE TYPE user_role_enum AS ENUM ('admin', 'member', 'viewer')")
    
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'])
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'])
    
    # Add new columns to users table
    op.add_column('users', sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('users', sa.Column('first_name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=64), nullable=True))
    op.add_column('users', sa.Column('role', sa.Enum('admin', 'member', 'viewer', name='user_role_enum'), nullable=True))
    
    # Rename hashed_password to password_hash for consistency
    op.alter_column('users', 'hashed_password', new_column_name='password_hash')
    
    # Update existing users to use tenant_id as organization_id
    op.execute("""
        INSERT INTO organizations (id, name, slug, is_active)
        SELECT DISTINCT t.id, t.name, t.slug, t.is_active
        FROM tenants t
        ON CONFLICT (id) DO NOTHING
    """)
    
    op.execute("""
        UPDATE users 
        SET organization_id = tenant_id,
            first_name = COALESCE(first_name, 'System'),
            last_name = COALESCE(last_name, 'User'),
            role = CASE 
                WHEN is_superuser THEN 'admin'::user_role_enum
                ELSE 'member'::user_role_enum
            END
        WHERE organization_id IS NULL
    """)
    
    # Make new columns non-nullable
    op.alter_column('users', 'organization_id', nullable=False)
    op.alter_column('users', 'first_name', nullable=False)
    op.alter_column('users', 'last_name', nullable=False)
    op.alter_column('users', 'role', nullable=False, server_default=sa.text("'member'::user_role_enum"))
    
    # Create foreign key
    op.create_foreign_key('fk_users_organization_id', 'users', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'])
    op.create_index(op.f('ix_users_role'), 'users', ['role'])
    
    # Update audit_logs table
    op.add_column('audit_logs', sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_audit_logs_organization_id', 'audit_logs', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_index(op.f('ix_audit_logs_organization_id'), 'audit_logs', ['organization_id'])
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'])
    op.create_index(op.f('ix_audit_logs_resource'), 'audit_logs', ['resource'])
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'])


def downgrade():
    # Remove indexes
    op.drop_index(op.f('ix_audit_logs_created_at'), 'audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource'), 'audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), 'audit_logs')
    op.drop_index(op.f('ix_audit_logs_organization_id'), 'audit_logs')
    op.drop_constraint('fk_audit_logs_organization_id', 'audit_logs', type_='foreignkey')
    op.drop_column('audit_logs', 'organization_id')
    
    op.drop_index(op.f('ix_users_role'), 'users')
    op.drop_index(op.f('ix_users_organization_id'), 'users')
    op.drop_constraint('fk_users_organization_id', 'users', type_='foreignkey')
    
    op.drop_column('users', 'role')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'organization_id')
    
    op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    
    op.drop_index(op.f('ix_organizations_slug'), 'organizations')
    op.drop_index(op.f('ix_organizations_name'), 'organizations')
    op.drop_table('organizations')
    
    op.execute("DROP TYPE user_role_enum")
