"""add user_agent to login_attempt

Revision ID: b3c4d5e6f7a8
Revises: a5b8089214d9
Create Date: 2026-07-29 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'a5b8089214d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'login_attempt',
        sa.Column('user_agent', sa.String(512), nullable=True),
        schema='users',
    )


def downgrade() -> None:
    op.drop_column('login_attempt', 'user_agent', schema='users')
