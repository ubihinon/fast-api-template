import datetime
import uuid
from typing import Annotated

from sqlalchemy import func, Index, String, text, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

from src.settings import sync_engine


class Base(DeclarativeBase):
    pass


# Base.metadata.drop_all(sync_engine)
Base.metadata.create_all(sync_engine)


UUIDPK = Annotated[UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
IntPK = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
CreatedAt = Annotated[
    datetime.datetime, mapped_column(server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"), nullable=False)
]
UpdatedAt = Annotated[
    datetime.datetime, mapped_column(
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        onupdate=datetime.datetime.now(datetime.UTC),
        nullable=False
    )
]


class User(Base):
    __tablename__ = 'user'

    id: Mapped[IntPK]
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        Index('ix_user_email_lower', func.lower(email), unique=True),
    )

    @validates('email')
    def validate_email(self, key, value):
        return value.strip().lower() if value else value
