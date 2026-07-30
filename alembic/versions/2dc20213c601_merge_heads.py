"""merge heads

Revision ID: 2dc20213c601
Revises: c4d5e6f7a8b9, df90e826ac72
Create Date: 2026-07-30 17:33:22.461709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2dc20213c601'
down_revision: Union[str, Sequence[str], None] = ('c4d5e6f7a8b9', 'df90e826ac72')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
