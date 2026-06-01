import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class IdIntPkMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class CreatedUpdatedMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now(), nullable=False,
    )
