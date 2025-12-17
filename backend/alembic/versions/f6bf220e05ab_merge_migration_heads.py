"""Merge migration heads

Revision ID: f6bf220e05ab
Revises: "('add_wifi_fields', 'bebe13c745a6')"
Create Date: 2025-12-16 17:29:50.978910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6bf220e05ab'
down_revision = ('add_wifi_fields', 'bebe13c745a6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
