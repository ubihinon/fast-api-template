"""remove unique constraint from login_code.code

Revision ID: 361d43af2ba9
Revises: a5b8089214d9
Create Date: 2026-07-28 13:31:13.065863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '361d43af2ba9'
down_revision: Union[str, Sequence[str], None] = 'a5b8089214d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_users_login_code_code'), table_name='login_code', schema='users')
    op.create_index(op.f('ix_users_login_code_code'), 'login_code', ['code'], unique=False, schema='users')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_login_code_code'), table_name='login_code', schema='users')
    op.create_index(op.f('ix_users_login_code_code'), 'login_code', ['code'], unique=True, schema='users')
