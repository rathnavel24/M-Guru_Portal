"""alter  table

Revision ID: a7357856d7af
Revises: 2bfb783585e5
Create Date: 2026-03-27 21:53:20.791240

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7357856d7af'
down_revision: Union[str, Sequence[str], None] = '2bfb783585e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
