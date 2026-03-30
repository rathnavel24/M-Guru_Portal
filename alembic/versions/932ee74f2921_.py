"""empty message

Revision ID: 932ee74f2921
Revises: 4dab7c692869, 8df271a08ae3
Create Date: 2026-03-30 14:07:21.822346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '932ee74f2921'
down_revision: Union[str, Sequence[str], None] = ('4dab7c692869', '8df271a08ae3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
