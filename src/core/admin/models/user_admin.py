from datetime import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins import CreatedUpdatedMixin


class UserAdmin(CreatedUpdatedMixin, Base):
    """
    Модель пользователя администратора
    """
    __tablename__ = "user_admin"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column()

    def __repr__(self) -> str:
        return f"<UserAdmin(id={self.id}, username='{self.username}', email='{self.email}')>"
# alembic revision --autogenerate -m "create user admin"
