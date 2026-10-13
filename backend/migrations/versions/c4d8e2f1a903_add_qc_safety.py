"""add inspections, inspection items, safety reports

Revision ID: c4d8e2f1a903
Revises: 7f3c1a9b5d20
Create Date: 2026-10-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d8e2f1a903'
down_revision: Union[str, Sequence[str], None] = '7f3c1a9b5d20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('inspection_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('category', sa.Enum('CONCRETE', 'REBAR', 'FORMWORK', 'OTHER', name='inspectioncategory'), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'PASSED', 'FAILED', name='inspectionstatus'), nullable=True),
        sa.Column('inspector', sa.String(length=255), nullable=True),
        sa.Column('inspected_at', sa.DateTime(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_inspections_project_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_inspections_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_inspections_project_id'), ['project_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_inspections_status'), ['status'], unique=False)

    op.create_table(
        'inspection_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inspection_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('standard', sa.String(length=100), nullable=True),
        sa.Column('result', sa.Enum('OK', 'NOT_OK', 'NA', name='checkresult'), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['inspection_id'], ['inspections.id'], name='fk_inspection_items_inspection_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('inspection_items', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_inspection_items_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_inspection_items_inspection_id'), ['inspection_id'], unique=False)

    op.create_table(
        'safety_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('report_number', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.Enum('INCIDENT', 'NEAR_MISS', 'UNSAFE_ACT', 'UNSAFE_CONDITION', name='safetycategory'), nullable=True),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity'), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('action_taken', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'INVESTIGATING', 'CLOSED', name='safetystatus'), nullable=True),
        sa.Column('reported_by', sa.String(length=255), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_safety_reports_project_id'),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('safety_reports', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_safety_reports_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_safety_reports_project_id'), ['project_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_safety_reports_status'), ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('safety_reports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_safety_reports_status'))
        batch_op.drop_index(batch_op.f('ix_safety_reports_project_id'))
        batch_op.drop_index(batch_op.f('ix_safety_reports_id'))
    op.drop_table('safety_reports')

    with op.batch_alter_table('inspection_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inspection_items_inspection_id'))
        batch_op.drop_index(batch_op.f('ix_inspection_items_id'))
    op.drop_table('inspection_items')

    with op.batch_alter_table('inspections', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_inspections_status'))
        batch_op.drop_index(batch_op.f('ix_inspections_project_id'))
        batch_op.drop_index(batch_op.f('ix_inspections_id'))
    op.drop_table('inspections')
