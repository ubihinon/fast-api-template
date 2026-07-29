"""add ip_address and last_used_at to access_token

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-07-29 00:01:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'access_token',
        sa.Column('ip_address', sa.String(45), nullable=True),
        schema='users',
    )
    op.add_column(
        'access_token',
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        schema='users',
    )


def downgrade() -> None:
    op.drop_column('access_token', 'last_used_at', schema='users')
    op.drop_column('access_token', 'ip_address', schema='users')
