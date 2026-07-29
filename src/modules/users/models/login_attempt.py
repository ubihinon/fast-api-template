import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.types import UserIdType


class LoginAttempt(Base):
    __tablename__ = "login_attempt"
    __table_args__ = (
        Index("ix_login_attempt_user_ip_correct_created", "user_id", "ip_address", "is_correct", "created_at"),
        {"schema": "users", "extend_existing": True},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[UserIdType] = mapped_column(
        Integer, ForeignKey("users.user.id", ondelete="cascade"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    code_entered: Mapped[str] = mapped_column(String(6), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
