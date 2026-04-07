"""changes Emi_amount to emi_amount in fee table

Revision ID: 8aba6da2440a
Revises: d8d01bac5258
Create Date: 2026-04-07 10:17:57.323262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8aba6da2440a'
down_revision: Union[str, Sequence[str], None] = 'd8d01bac5258'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename column Emi_amount -> emi_amount
    op.alter_column(
        'fees',
        'Emi_amount',
        new_column_name='emi_amount'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert column name back
    op.alter_column(
        'fees',
        'emi_amount',
        new_column_name='Emi_amount'
    )