"""merge heads

Revision ID: 5a1c396caf49
Revises: 6c011d885fdd, 9d6b26dd8b7d
Create Date: 2026-04-01 11:24:52.069571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a1c396caf49'
down_revision: Union[str, Sequence[str], None] = ('6c011d885fdd', '9d6b26dd8b7d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
