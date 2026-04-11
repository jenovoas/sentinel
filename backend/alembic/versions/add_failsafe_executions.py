"""add failsafe executions

Revision ID: add_failsafe_exec
Revises: bebe13c745a6
Create Date: 2025-04-11 03:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_failsafe_exec'
down_revision = 'bebe13c745a6'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('failsafe_executions',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('playbook', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('triggered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('triggered_by', sa.String(length=255), nullable=False),
    sa.Column('severity', sa.String(length=50), nullable=False),
    sa.Column('outcome', sa.String(length=500), nullable=True),
    sa.Column('context_data', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_failsafe_executions_playbook'), 'failsafe_executions', ['playbook'], unique=False)
    op.create_index(op.f('ix_failsafe_executions_status'), 'failsafe_executions', ['status'], unique=False)
    op.create_index(op.f('ix_failsafe_executions_triggered_at'), 'failsafe_executions', ['triggered_at'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_failsafe_executions_triggered_at'), table_name='failsafe_executions')
    op.drop_index(op.f('ix_failsafe_executions_status'), table_name='failsafe_executions')
    op.drop_index(op.f('ix_failsafe_executions_playbook'), table_name='failsafe_executions')
    op.drop_table('failsafe_executions')
