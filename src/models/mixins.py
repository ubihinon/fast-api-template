import datetime

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column


class IdIntPkMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class CreatedUpdatedMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        onupdate=datetime.datetime.now(datetime.UTC),
        nullable=False
    )
