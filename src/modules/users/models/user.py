from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Index
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import validates

from core.models.base import Base
from core.models.mixins import CreatedUpdatedMixin, IdIntPkMixin
from core.models.types import UserIdType


class User(IdIntPkMixin, CreatedUpdatedMixin, SQLAlchemyBaseUserTable[UserIdType], Base):
    __table_args__ = (
        Index('ix_user_email', SQLAlchemyBaseUserTable.email, unique=True),
        {"schema": "users", "extend_existing": True},
    )

    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyUserDatabase(session, cls)

    @validates("email")
    def validate_email(self, key, value):
        return value.strip().lower() if value else value
