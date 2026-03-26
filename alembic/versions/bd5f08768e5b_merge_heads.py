"""merge heads

Revision ID: bd5f08768e5b
Revises: 87824d28f2d5, d084f0a8690a
Create Date: 2026-03-26 11:06:11.259243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd5f08768e5b'
down_revision: Union[str, Sequence[str], None] = ('87824d28f2d5', 'd084f0a8690a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
