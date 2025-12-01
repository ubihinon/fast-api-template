"""empty message

Revision ID: 77f475d06aae
Revises: a6e5c269de6a
Create Date: 2025-12-01 22:42:10.182387

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "77f475d06aae"
down_revision: Union[str, Sequence[str], None] = "a6e5c269de6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "user",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text(
            "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC'::text)"
        ),
    )
    op.alter_column(
        "user",
        "updated_at",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False,
        existing_server_default=sa.text(
            "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC'::text)"
        ),
    )


def downgrade() -> None:
    op.alter_column(
        "user",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text(
            "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC'::text)"
        ),
    )
    op.alter_column(
        "user",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False,
        existing_server_default=sa.text(
            "(CURRENT_TIMESTAMP AT TIME ZONE 'UTC'::text)"
        ),
    )
