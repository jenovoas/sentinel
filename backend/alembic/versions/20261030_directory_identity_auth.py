"""Use Samba AD as the credential authority for tenant user mappings."""

from alembic import op
import sqlalchemy as sa


revision = "20261030_directory_identity_auth"
down_revision = "20261029_user_timestamp_defaults"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("directory_id", sa.String(length=36), nullable=True))
    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=True)

    # Password hashes are deliberately removed: AD is the sole human credential
    # authority. A pre-change database backup is the only rollback for this data.
    op.execute("UPDATE users SET password_hash = NULL")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.create_unique_constraint(
        "uq_users_org_email", "users", ["organization_id", "email"]
    )
    op.create_unique_constraint(
        "uq_users_org_username", "users", ["organization_id", "username"]
    )
    op.create_unique_constraint(
        "uq_users_org_directory_id", "users", ["organization_id", "directory_id"]
    )


def downgrade() -> None:
    raise RuntimeError(
        "AD adoption clears local password hashes; restore the protected pre-change "
        "database backup to roll back instead of running an Alembic downgrade."
    )
