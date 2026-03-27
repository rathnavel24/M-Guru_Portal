"""alter  table1

Revision ID: 86f79aa3adeb
Revises: a7357856d7af
Create Date: 2026-03-27 21:56:16.287874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86f79aa3adeb'
down_revision: Union[str, Sequence[str], None] = 'a7357856d7af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
