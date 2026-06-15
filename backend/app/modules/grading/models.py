"""Модель отправленной работы (submission).

Универсальна для трёх механик проверки:
  • квиз    — ответы в payload_json, автопроверка;
  • код     — исходник в code, прогон в песочнице, вердикт + result_json;
  • проект  — файл/ссылка в file_url, ручная проверка преподавателем.
"""
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum as SaEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin
from app.db.enums import CodeVerdict, SubmissionStatus


class Submission(IdMixin, Base):
    __tablename__ = "submissions"

    assignment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    student_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("student_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Полезная нагрузка под тип задания
    payload_json: Mapped[dict | list | None] = mapped_column(JSONB)  # ответы квиза
    code: Mapped[str | None] = mapped_column(Text)                    # исходник код-задания
    file_url: Mapped[str | None] = mapped_column(String(512))         # путь к проекту (локальный том)

    # Состояние и результат
    status: Mapped[SubmissionStatus] = mapped_column(
        SaEnum(SubmissionStatus, native_enum=False, length=20),
        default=SubmissionStatus.QUEUED,
        nullable=False,
        index=True,
    )
    verdict: Mapped[CodeVerdict | None] = mapped_column(
        SaEnum(CodeVerdict, native_enum=False, length=16)
    )
    result_json: Mapped[dict | list | None] = mapped_column(JSONB)  # детализация по тест-кейсам
    score: Mapped[int | None] = mapped_column(Integer)
    feedback: Mapped[str | None] = mapped_column(Text)

    # Кто и когда проверил (для проектов — преподаватель)
    checked_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("teacher_profiles.user_id", ondelete="SET NULL")
    )
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
