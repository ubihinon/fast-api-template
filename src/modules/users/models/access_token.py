import datetime

from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.types import UserIdType


class ActiveAccessTokenDatabase(SQLAlchemyAccessTokenDatabase):
    """Extends fastapi-users' default token DB to filter out inactive tokens.

    The default get_by_token only checks the token string and creation date —
    it ignores our is_active flag, so logout (which sets is_active=False)
    would not actually invalidate the session. This subclass adds the filter.
    """

    async def get_by_token(
        self, token: str, max_age: datetime.datetime | None = None
    ):
        statement = select(self.access_token_table).where(
            self.access_token_table.token == token,
            self.access_token_table.is_active.is_(True),
        )
        if max_age is not None:
            statement = statement.where(
                self.access_token_table.created_at >= max_age
            )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()


class AccessToken(SQLAlchemyBaseAccessTokenTable[UserIdType], Base):
    __tablename__ = "access_token"
    __table_args__ = {"schema": "users", "extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    user_id: Mapped[UserIdType] = mapped_column(
        Integer, ForeignKey("users.user.id", ondelete="cascade"), nullable=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    @classmethod
    def get_db(cls, session: AsyncSession):
        return ActiveAccessTokenDatabase(session, cls)
