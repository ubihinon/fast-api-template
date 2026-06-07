import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, func, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.types import UserIdType


class LoginCode(Base):
    __tablename__ = "login_code"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)
    user_id: Mapped[UserIdType] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
