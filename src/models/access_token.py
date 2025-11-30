from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTable
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from api.types.user_id import UserIdType
from models.base import Base

from sqlalchemy.ext.asyncio import AsyncSession


class AccessToken(SQLAlchemyBaseAccessTokenTable[UserIdType], Base):
    user_id: Mapped[UserIdType] = mapped_column(
        Integer, ForeignKey('user.id', ondelete='cascade'), nullable=False
    )

    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyAccessTokenDatabase(session, cls)
