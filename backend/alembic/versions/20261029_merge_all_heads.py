"""Merge the remaining Alembic migration heads."""

revision = "20261029_merge_all_heads"
down_revision = ("dd222c78d329", "merge_auth_monitoring_heads")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
