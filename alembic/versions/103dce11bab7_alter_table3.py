"""alter  table3

Revision ID: 103dce11bab7
Revises: bfa46e3f1d30
Create Date: 2026-03-27 22:07:51.210236

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '103dce11bab7'
down_revision: Union[str, Sequence[str], None] = 'bfa46e3f1d30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('token', sa.Column('last_activity', sa.TIMESTAMP(), nullable=True))
    op.add_column('token', sa.Column('productive_minutes', sa.Float(), nullable=True, server_default='0'))
    op.add_column('token', sa.Column('status', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('token', 'status')
    op.drop_column('token', 'productive_minutes')
    op.drop_column('token', 'last_activity')
