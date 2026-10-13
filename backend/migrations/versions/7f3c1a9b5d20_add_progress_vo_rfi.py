"""add progress entries, variation orders, rfis

Revision ID: 7f3c1a9b5d20
Revises: 52faea205d6f
Create Date: 2026-10-13 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f3c1a9b5d20'
down_revision: Union[str, Sequence[str], None] = '52faea205d6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'progress_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('planned_pct', sa.Float(), nullable=True),
        sa.Column('actual_pct', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_progress_entries_project_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('progress_entries', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_progress_entries_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_progress_entries_project_id'), ['project_id'], unique=False)

    op.create_table(
        'variation_orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('vo_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', name='vostatus'), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('change_region_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_variation_orders_project_id'),
        sa.ForeignKeyConstraint(['change_region_id'], ['change_regions.id'], name='fk_variation_orders_change_region_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('variation_orders', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_variation_orders_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_variation_orders_project_id'), ['project_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_variation_orders_status'), ['status'], unique=False)

    op.create_table(
        'rfis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('rfi_number', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'ANSWERED', 'CLOSED', name='rfistatus'), nullable=True),
        sa.Column('variation_order_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_rfis_project_id'),
        sa.ForeignKeyConstraint(['variation_order_id'], ['variation_orders.id'], name='fk_rfis_variation_order_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('rfis', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_rfis_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_rfis_project_id'), ['project_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_rfis_status'), ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('rfis', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_rfis_status'))
        batch_op.drop_index(batch_op.f('ix_rfis_project_id'))
        batch_op.drop_index(batch_op.f('ix_rfis_id'))
    op.drop_table('rfis')

    with op.batch_alter_table('variation_orders', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_variation_orders_status'))
        batch_op.drop_index(batch_op.f('ix_variation_orders_project_id'))
        batch_op.drop_index(batch_op.f('ix_variation_orders_id'))
    op.drop_table('variation_orders')

    with op.batch_alter_table('progress_entries', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_progress_entries_project_id'))
        batch_op.drop_index(batch_op.f('ix_progress_entries_id'))
    op.drop_table('progress_entries')
