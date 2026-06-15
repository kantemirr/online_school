"""Pydantic-схемы заданий, отправок и проверки."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.db.enums import AssignmentType, CodeVerdict, QuestionKind, SubmissionStatus


# ── Получение задания для решения ────────────────────────────────────────────
class QuestionForSolveOut(BaseModel):
    id: int
    text: str
    kind: QuestionKind
    options: Any  # варианты без правильных ответов


class CodeExampleOut(BaseModel):
    stdin: str | None
    expected_stdout: str


class AssignmentForSolveOut(BaseModel):
    id: int
    type: AssignmentType
    title: str
    max_score: int
    questions: list[QuestionForSolveOut] = Field(default_factory=list)
    examples: list[CodeExampleOut] = Field(default_factory=list)  # видимые тесты как примеры


# ── Отправка работ ───────────────────────────────────────────────────────────
class QuizSubmitIn(BaseModel):
    # {question_id (строкой): ответ} — список индексов или список пар
    answers: dict[str, Any]


class CodeSubmitIn(BaseModel):
    code: str = Field(min_length=1, max_length=20000)


class ProjectSubmitIn(BaseModel):
    link: str | None = Field(default=None, max_length=512)


# ── Результат отправки / опрос ───────────────────────────────────────────────
class SubmissionOut(BaseModel):
    id: int
    assignment_id: int
    status: SubmissionStatus
    verdict: CodeVerdict | None = None
    score: int | None = None
    feedback: str | None = None
    result_json: Any = None  # уже безопасный (без скрытых эталонов)
    created_at: datetime
    checked_at: datetime | None = None


# ── ИИ-подсказка ─────────────────────────────────────────────────────────────
class HintOut(BaseModel):
    hint: str
    source: Literal["ai", "heuristic"]


# ── Ручная проверка проектов ─────────────────────────────────────────────────
class GradingQueueItem(BaseModel):
    submission_id: int
    assignment_id: int
    student_id: int
    file_url: str | None
    created_at: datetime


class ReviewIn(BaseModel):
    score: int = Field(ge=0)
    feedback: str | None = None
    status: Literal["reviewed", "needs_revision"]
