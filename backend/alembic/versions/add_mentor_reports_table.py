"""add mentor_reports table

Revision ID: add_mentor_reports_table
Revises: add_phases_and_phase_id_to_sub_goals
Create Date: 2026-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_mentor_reports_table'
down_revision: Union[str, Sequence[str], None] = 'add_phases_and_phase_id_to_sub_goals'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'mentor_reports',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('time_frame', sa.String(), nullable=False, server_default='last_1_week'),
        sa.Column('short_report', sa.Text(), nullable=False),
        sa.Column('full_report', sa.Text(), nullable=False),
        sa.Column('context_summary', sa.Text(), nullable=True),
        sa.Column('neglected_goals', sa.Text(), nullable=True),
        sa.Column('report_date', sa.Date(), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('mentor_reports')
