from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app_types.user_id import UserIdType
from models.base import Base
from models.mixins import CreatedUpdatedMixin, IdIntPkMixin


# class User(Base):
#     __tablename__ = 'user'
#
#     id: Mapped[IntPK]
#     email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     is_active: Mapped[bool] = mapped_column(default=False)
#     created_at: Mapped[CreatedAt]
#     updated_at: Mapped[UpdatedAt]
#
#     __table_args__ = (
#         Index('ix_user_email_lower', func.lower(email), unique=True),
#     )
#
#     @validates('email')
#     def validate_email(self, key, value):
#         return value.strip().lower() if value else value


class User(IdIntPkMixin, CreatedUpdatedMixin, SQLAlchemyBaseUserTable[UserIdType], Base):
    @classmethod
    def get_db(cls, session: AsyncSession):
        return SQLAlchemyUserDatabase(session, cls)
