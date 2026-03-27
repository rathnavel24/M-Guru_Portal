"""alter  table2

Revision ID: bfa46e3f1d30
Revises: 86f79aa3adeb
Create Date: 2026-03-27 22:02:41.641776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfa46e3f1d30'
down_revision: Union[str, Sequence[str], None] = '86f79aa3adeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('tech_stack', sa.String(), nullable=True))
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'tech_stack')
    op.drop_column('users', 'phone')
