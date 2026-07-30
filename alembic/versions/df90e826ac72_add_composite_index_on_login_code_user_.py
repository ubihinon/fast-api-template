"""add composite index on login_code user_active_expires

Revision ID: df90e826ac72
Revises: 361d43af2ba9
Create Date: 2026-07-28 13:51:15.073842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df90e826ac72'
down_revision: Union[str, Sequence[str], None] = '361d43af2ba9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index('ix_login_code_user_active_expires', 'login_code', ['user_id', 'is_active', 'expires_at'], unique=False, schema='users')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_login_code_user_active_expires', table_name='login_code', schema='users')
