"""Модели геймификации: справочник достижений и факт их получения."""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin


class Achievement(IdMixin, Base):
    """Справочник достижений. condition_json описывает условие выдачи."""

    __tablename__ = "achievements"

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(255))
    condition_json: Mapped[dict | None] = mapped_column(JSONB)

    awards: Mapped[list["StudentAchievement"]] = relationship(
        back_populates="achievement", cascade="all, delete-orphan"
    )


class StudentAchievement(Base):
    """Факт получения достижения учеником (ассоциативная таблица)."""

    __tablename__ = "student_achievements"

    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student_profiles.user_id", ondelete="CASCADE"), primary_key=True
    )
    achievement_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    achievement: Mapped["Achievement"] = relationship(back_populates="awards")
