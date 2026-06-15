"""Модели каталога: иерархия Курс → Модуль → Урок → Задание → Вопросы/Тесты."""
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Enum as SaEnum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin
from app.db.enums import AssignmentType, CourseLevel, CourseTrack, QuestionKind


class Course(IdMixin, TimestampMixin, Base):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    track: Mapped[CourseTrack] = mapped_column(
        SaEnum(CourseTrack, native_enum=False, length=20), nullable=False, index=True
    )
    age_min: Mapped[int] = mapped_column(SmallInteger, default=8, nullable=False)
    age_max: Mapped[int] = mapped_column(SmallInteger, default=14, nullable=False)
    level: Mapped[CourseLevel] = mapped_column(
        SaEnum(CourseLevel, native_enum=False, length=20), nullable=False
    )
    cover_url: Mapped[str | None] = mapped_column(String(512))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)

    modules: Mapped[list["Module"]] = relationship(
        back_populates="course", order_by="Module.order_index", cascade="all, delete-orphan"
    )


class Module(IdMixin, Base):
    __tablename__ = "modules"
    __table_args__ = (UniqueConstraint("course_id", "order_index", name="uq_modules_course_order"),)

    course_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="module", order_by="Lesson.order_index", cascade="all, delete-orphan"
    )


class Lesson(IdMixin, Base):
    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("module_id", "order_index", name="uq_lessons_module_order"),)

    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    theory_md: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(String(512))

    module: Mapped["Module"] = relationship(back_populates="lessons")
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )


class Assignment(IdMixin, Base):
    __tablename__ = "assignments"

    lesson_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[AssignmentType] = mapped_column(
        SaEnum(AssignmentType, native_enum=False, length=16), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    max_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    lesson: Mapped["Lesson"] = relationship(back_populates="assignments")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )
    code_tests: Mapped[list["CodeTest"]] = relationship(
        back_populates="assignment", cascade="all, delete-orphan"
    )


class Question(IdMixin, Base):
    """Вопрос квиза. options_json — варианты, correct_json — эталон ответа."""

    __tablename__ = "questions"

    assignment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[QuestionKind] = mapped_column(
        SaEnum(QuestionKind, native_enum=False, length=16), nullable=False
    )
    options_json: Mapped[dict | list | None] = mapped_column(JSONB)
    correct_json: Mapped[dict | list | None] = mapped_column(JSONB)

    assignment: Mapped["Assignment"] = relationship(back_populates="questions")


class CodeTest(IdMixin, Base):
    """Тест-кейс для код-задания: вход и ожидаемый вывод."""

    __tablename__ = "code_tests"

    assignment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stdin: Mapped[str | None] = mapped_column(Text)
    expected_stdout: Mapped[str] = mapped_column(Text, nullable=False)
    # Скрытый тест не показывается ученику (безопасный фидбек)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    assignment: Mapped["Assignment"] = relationship(back_populates="code_tests")
