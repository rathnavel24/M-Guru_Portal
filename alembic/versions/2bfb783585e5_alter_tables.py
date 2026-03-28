"""alter  tables

Revision ID: 2bfb783585e5
Revises: f37f4fc308ba
Create Date: 2026-03-27 21:50:54.945817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bfb783585e5'
down_revision: Union[str, Sequence[str], None] = 'f37f4fc308ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
