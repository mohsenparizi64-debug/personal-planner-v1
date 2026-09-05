"""add suggested_due_date to tasks

Revision ID: add_suggested_due_date
Revises: 638aab5133c2
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_suggested_due_date'
down_revision = '638aab5133c2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'tasks',
        sa.Column('suggested_due_date', sa.Date(), nullable=True)
    )


def downgrade():
    op.drop_column('tasks', 'suggested_due_date')
