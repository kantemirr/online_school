"""Модели прохождения: запись на курс и прогресс по урокам."""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SaEnum,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin
from app.db.enums import EnrollmentStatus, LessonProgressStatus


class Enrollment(IdMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_enrollments_student_course"),
    )

    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        SaEnum(EnrollmentStatus, native_enum=False, length=16),
        default=EnrollmentStatus.ACTIVE,
        nullable=False,
    )
    progress_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lesson_progress: Mapped[list["LessonProgress"]] = relationship(
        back_populates="enrollment", cascade="all, delete-orphan"
    )


class LessonProgress(IdMixin, Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (
        UniqueConstraint("enrollment_id", "lesson_id", name="uq_lesson_progress_enrollment_lesson"),
    )

    enrollment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lesson_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[LessonProgressStatus] = mapped_column(
        SaEnum(LessonProgressStatus, native_enum=False, length=16),
        default=LessonProgressStatus.NOT_STARTED,
        nullable=False,
    )
    score: Mapped[int | None] = mapped_column(Integer)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    enrollment: Mapped["Enrollment"] = relationship(back_populates="lesson_progress")
