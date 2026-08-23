"""add phases and phase_id to sub_goals

Revision ID: add_phases_and_phase_id_to_sub_goals
Revises: 638aab5133c2
Create Date: 2026-08-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_phases_and_phase_id_to_sub_goals'
down_revision = '638aab5133c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'phases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_id', sa.Integer(), sa.ForeignKey('goals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(), nullable=True, server_default='not_started'),
        sa.Column('progress_percent', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('order_index', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('color', sa.String(), nullable=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('sub_goals', sa.Column('phase_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_sub_goals_phase_id_phases',
        'sub_goals', 'phases',
        ['phase_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_sub_goals_phase_id_phases', 'sub_goals', type_='foreignkey')
    op.drop_column('sub_goals', 'phase_id')
    op.drop_table('phases')
