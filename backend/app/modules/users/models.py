"""Модели домена пользователей: учётные записи и профили ролей.

Структура: единая таблица users (учётные данные + роль) и отдельные
профили под каждую роль (1:1 с users). Аккаунт ребёнка управляется
родителем (parent_id), данные минимизированы согласно ФЗ-152.
"""
from datetime import date

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    Enum as SaEnum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin
from app.db.enums import AgeGroup, UserRole


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SaEnum(UserRole, native_enum=False, length=20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    parent_profile: Mapped["ParentProfile | None"] = relationship(back_populates="user", uselist=False)
    student_profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user", uselist=False, foreign_keys="StudentProfile.user_id"
    )
    teacher_profile: Mapped["TeacherProfile | None"] = relationship(back_populates="user", uselist=False)


class ParentProfile(TimestampMixin, Base):
    __tablename__ = "parent_profiles"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32))
    # Согласие на обработку ПДн (в т.ч. данных ребёнка) — ФЗ-152
    consent_pdn: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="parent_profile")
    children: Mapped[list["StudentProfile"]] = relationship(
        back_populates="parent", foreign_keys="StudentProfile.parent_id"
    )


class StudentProfile(TimestampMixin, Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("parent_profiles.user_id", ondelete="SET NULL"), index=True
    )
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    age_group: Mapped[AgeGroup] = mapped_column(SaEnum(AgeGroup, native_enum=False, length=16), nullable=False)

    # Упрощённый вход ребёнка под контролем родителя
    login_username: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    pin_hash: Mapped[str | None] = mapped_column(String(255))

    # Геймификация
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="student_profile", foreign_keys=[user_id])
    parent: Mapped["ParentProfile | None"] = relationship(
        back_populates="children", foreign_keys=[parent_id]
    )


class TeacherProfile(TimestampMixin, Base):
    __tablename__ = "teacher_profiles"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    specialization: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(String(2000))

    user: Mapped["User"] = relationship(back_populates="teacher_profile")
