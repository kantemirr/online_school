"""Модели групп, расписания онлайн-занятий и посещаемости.

Видеоконференция задаётся ссылкой (meeting_url) — преподаватель вставляет
ссылку Zoom/Jitsi; полноценная интеграция вне границ системы.
"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SaEnum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin
from app.db.enums import AttendanceStatus


class Group(IdMixin, Base):
    __tablename__ = "groups"

    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teacher_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    members: Mapped[list["GroupMember"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["ScheduleSession"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class GroupMember(Base):
    __tablename__ = "group_members"

    group_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student_profiles.user_id", ondelete="CASCADE"), primary_key=True
    )

    group: Mapped["Group"] = relationship(back_populates="members")


class ScheduleSession(IdMixin, Base):
    __tablename__ = "schedule_sessions"

    group_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    teacher_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("teacher_profiles.user_id", ondelete="CASCADE"), nullable=False
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    meeting_url: Mapped[str | None] = mapped_column(String(512))

    group: Mapped["Group"] = relationship(back_populates="sessions")
    attendance: Mapped[list["Attendance"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class Attendance(Base):
    __tablename__ = "attendance"

    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("schedule_sessions.id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student_profiles.user_id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[AttendanceStatus] = mapped_column(
        SaEnum(AttendanceStatus, native_enum=False, length=16),
        default=AttendanceStatus.ABSENT,
        nullable=False,
    )

    session: Mapped["ScheduleSession"] = relationship(back_populates="attendance")
