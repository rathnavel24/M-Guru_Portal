"""empty message

Revision ID: 2cf0d9b76634
Revises: 7aaaa2058b01, bacb5e559fde
Create Date: 2026-04-03 17:26:25.375122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cf0d9b76634'
down_revision: Union[str, Sequence[str], None] = ('7aaaa2058b01', 'bacb5e559fde')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
