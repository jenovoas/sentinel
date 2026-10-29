"""Restore server defaults for user audit timestamps."""

from alembic import op
import sqlalchemy as sa

revision = "20261029_user_timestamp_defaults"
down_revision = "20261029_merge_all_heads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "created_at", server_default=sa.text("now()"))
    op.alter_column("users", "updated_at", server_default=sa.text("now()"))


def downgrade() -> None:
    op.alter_column("users", "updated_at", server_default=None)
    op.alter_column("users", "created_at", server_default=None)
