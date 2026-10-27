"""Merge the existing monitoring and WiFi migration branches."""

revision = "merge_auth_monitoring_heads"
down_revision = ("add_wifi_fields", "bebe13c745a6")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
