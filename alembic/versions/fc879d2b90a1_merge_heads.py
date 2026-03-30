"""merge heads

Revision ID: fc879d2b90a1
Revises: 6c011d885fdd, 9d6b26dd8b7d
Create Date: 2026-03-30 23:52:36.792660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc879d2b90a1'
down_revision: Union[str, Sequence[str], None] = ('6c011d885fdd', '9d6b26dd8b7d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
