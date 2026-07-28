"""add index on login_attempt user_ip_correct_created

Revision ID: a5b8089214d9
Revises: a1b2c3d4e5f6
Create Date: 2026-07-28 13:10:40.267079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5b8089214d9'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_user_admin_email'), table_name='user_admin', schema='admin')
    op.drop_index(op.f('ix_user_admin_id'), table_name='user_admin', schema='admin')
    op.drop_index(op.f('ix_user_admin_username'), table_name='user_admin', schema='admin')
    op.create_index(op.f('ix_admin_user_admin_email'), 'user_admin', ['email'], unique=True, schema='admin')
    op.create_index(op.f('ix_admin_user_admin_id'), 'user_admin', ['id'], unique=False, schema='admin')
    op.create_index(op.f('ix_admin_user_admin_username'), 'user_admin', ['username'], unique=True, schema='admin')
    op.drop_index(op.f('ix_access_token_token'), table_name='access_token', schema='users')
    op.create_index(op.f('ix_users_access_token_token'), 'access_token', ['token'], unique=True, schema='users')
    op.create_index('ix_login_attempt_user_ip_correct_created', 'login_attempt', ['user_id', 'ip_address', 'is_correct', 'created_at'], unique=False, schema='users')
    op.drop_index(op.f('ix_login_code_code'), table_name='login_code', schema='users')
    op.create_index(op.f('ix_users_login_code_code'), 'login_code', ['code'], unique=True, schema='users')
    op.create_index(op.f('ix_users_user_email'), 'user', ['email'], unique=True, schema='users')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_user_email'), table_name='user', schema='users')
    op.drop_index(op.f('ix_users_login_code_code'), table_name='login_code', schema='users')
    op.create_index(op.f('ix_login_code_code'), 'login_code', ['code'], unique=True, schema='users')
    op.drop_index('ix_login_attempt_user_ip_correct_created', table_name='login_attempt', schema='users')
    op.drop_index(op.f('ix_users_access_token_token'), table_name='access_token', schema='users')
    op.create_index(op.f('ix_access_token_token'), 'access_token', ['token'], unique=True, schema='users')
    op.drop_index(op.f('ix_admin_user_admin_username'), table_name='user_admin', schema='admin')
    op.drop_index(op.f('ix_admin_user_admin_id'), table_name='user_admin', schema='admin')
    op.drop_index(op.f('ix_admin_user_admin_email'), table_name='user_admin', schema='admin')
    op.create_index(op.f('ix_user_admin_username'), 'user_admin', ['username'], unique=True, schema='admin')
    op.create_index(op.f('ix_user_admin_id'), 'user_admin', ['id'], unique=False, schema='admin')
    op.create_index(op.f('ix_user_admin_email'), 'user_admin', ['email'], unique=True, schema='admin')
