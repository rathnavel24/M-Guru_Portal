"""merge heads

Revision ID: 8e60aba645ba
Revises: 4dab7c692869, 8df271a08ae3
Create Date: 2026-03-30 01:18:45.714752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e60aba645ba'
down_revision: Union[str, Sequence[str], None] = ('4dab7c692869', '8df271a08ae3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
