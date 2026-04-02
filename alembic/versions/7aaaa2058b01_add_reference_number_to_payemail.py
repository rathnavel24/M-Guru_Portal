"""add reference number to payemail

Revision ID: 7aaaa2058b01
Revises: fc879d2b90a1
Create Date: 2026-03-30
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '7aaaa2058b01'
down_revision: Union[str, Sequence[str], None] = 'fc879d2b90a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ✅ ONLY what you need
    op.add_column(
        'pay_email',
        sa.Column('reference_no', sa.String(length=255))
    )


def downgrade() -> None:
    op.drop_column('pay_email', 'reference_no')