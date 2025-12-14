"""Add WiFi fields to metric_samples

Revision ID: add_wifi_fields
Revises: 4c53459a200b
Create Date: 2025-12-13 23:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_wifi_fields'
down_revision = '4c53459a200b'
branch_labels = None
depends_on = None


def upgrade():
    # Add WiFi columns to metric_samples
    op.add_column('metric_samples', sa.Column('wifi_ssid', sa.String(length=255), nullable=True))
    op.add_column('metric_samples', sa.Column('wifi_signal', sa.Integer(), nullable=True))
    op.add_column('metric_samples', sa.Column('wifi_connected', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    # Create indexes for WiFi data
    op.create_index(op.f('ix_metric_samples_wifi_connected'), 'metric_samples', ['wifi_connected'])


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_metric_samples_wifi_connected'), 'metric_samples')
    
    # Drop columns
    op.drop_column('metric_samples', 'wifi_connected')
    op.drop_column('metric_samples', 'wifi_signal')
    op.drop_column('metric_samples', 'wifi_ssid')
