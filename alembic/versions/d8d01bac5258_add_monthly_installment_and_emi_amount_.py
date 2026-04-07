"""add monthly installment and emi amount to fee table

Revision ID: d8d01bac5258
Revises: 72c6dd9ce04b
Create Date: 2026-04-06

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'd8d01bac5258'
down_revision: Union[str, Sequence[str], None] = '72c6dd9ce04b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✅ Only add columns
    op.add_column(
        'fees',
        sa.Column('monthly_installment', sa.Boolean(), nullable=True)
    )
    op.add_column(
        'fees',
        sa.Column('emi_amount', sa.Float(), nullable=True)
    )


def downgrade() -> None:
    # ✅ Reverse only what we added
    op.drop_column('fees', 'emi_amount')
    op.drop_column('fees', 'monthly_installment')
    # ### end Alembic commands ###
