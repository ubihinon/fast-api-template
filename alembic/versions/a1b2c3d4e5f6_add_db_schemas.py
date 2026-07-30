"""add db schemas (users, admin)

Revision ID: a1b2c3d4e5f6
Revises: ed794e84152a
Create Date: 2026-07-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'ed794e84152a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS users")
    op.execute("CREATE SCHEMA IF NOT EXISTS admin")

    op.execute("ALTER TABLE public.user SET SCHEMA users")
    op.execute("ALTER TABLE public.access_token SET SCHEMA users")
    op.execute("ALTER TABLE public.login_code SET SCHEMA users")
    op.execute("ALTER TABLE public.login_attempt SET SCHEMA users")
    op.execute("ALTER TABLE public.user_admin SET SCHEMA admin")


def downgrade() -> None:
    op.execute("ALTER TABLE users.user SET SCHEMA public")
    op.execute("ALTER TABLE users.access_token SET SCHEMA public")
    op.execute("ALTER TABLE users.login_code SET SCHEMA public")
    op.execute("ALTER TABLE users.login_attempt SET SCHEMA public")
    op.execute("ALTER TABLE admin.user_admin SET SCHEMA public")

    op.execute("DROP SCHEMA IF EXISTS users")
    op.execute("DROP SCHEMA IF EXISTS admin")
