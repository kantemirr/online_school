"""Pydantic-схемы каталога: чтение (витрина) и админ-управление контентом."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.db.enums import AssignmentType, CourseLevel, CourseTrack, QuestionKind

# Человекочитаемые подписи направлений
TRACK_LABELS: dict[CourseTrack, str] = {
    CourseTrack.SCRATCH: "Scratch",
    CourseTrack.PYTHON: "Python",
    CourseTrack.WEB: "Веб-разработка",
    CourseTrack.GAMEDEV: "Создание игр",
    CourseTrack.ALGORITHMS: "Алгоритмика",
}


# ── Публичное чтение ─────────────────────────────────────────────────────────
class TrackOut(BaseModel):
    code: CourseTrack
    label: str
    course_count: int


class CourseSummaryOut(BaseModel):
    id: int
    title: str
    description: str | None
    track: CourseTrack
    age_min: int
    age_max: int
    level: CourseLevel
    cover_url: str | None
    price: Decimal


class LessonNodeOut(BaseModel):
    id: int
    title: str
    order_index: int
    assignment_count: int


class ModuleNodeOut(BaseModel):
    id: int
    title: str
    order_index: int
    lessons: list[LessonNodeOut]


class CourseDetailOut(CourseSummaryOut):
    module_count: int
    lesson_count: int
    modules: list[ModuleNodeOut]


class CourseListOut(BaseModel):
    items: list[CourseSummaryOut]
    total: int
    page: int
    size: int


# ── Админ-управление ─────────────────────────────────────────────────────────
class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    track: CourseTrack
    age_min: int = Field(default=8, ge=4, le=18)
    age_max: int = Field(default=14, ge=4, le=18)
    level: CourseLevel = CourseLevel.BEGINNER
    cover_url: str | None = Field(default=None, max_length=512)
    price: Decimal = Field(default=Decimal("0.00"), ge=0)


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    track: CourseTrack | None = None
    age_min: int | None = Field(default=None, ge=4, le=18)
    age_max: int | None = Field(default=None, ge=4, le=18)
    level: CourseLevel | None = None
    cover_url: str | None = Field(default=None, max_length=512)
    price: Decimal | None = Field(default=None, ge=0)


class ModuleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    order_index: int | None = None  # None → авто-следующий


class ModuleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    order_index: int | None = None


class LessonCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    order_index: int | None = None
    theory_md: str | None = None
    video_url: str | None = Field(default=None, max_length=512)


class LessonUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    order_index: int | None = None
    theory_md: str | None = None
    video_url: str | None = Field(default=None, max_length=512)


class QuestionCreate(BaseModel):
    text: str = Field(min_length=1)
    kind: QuestionKind
    options_json: list | dict | None = None
    correct_json: list | dict | None = None


class CodeTestCreate(BaseModel):
    stdin: str | None = None
    expected_stdout: str
    is_hidden: bool = False
    weight: int = Field(default=1, ge=1)


class AssignmentCreate(BaseModel):
    type: AssignmentType
    title: str = Field(min_length=1, max_length=255)
    max_score: int = Field(default=100, ge=1)
    due_at: datetime | None = None
    questions: list[QuestionCreate] = Field(default_factory=list)
    code_tests: list[CodeTestCreate] = Field(default_factory=list)


class AssignmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    max_score: int | None = Field(default=None, ge=1)
    due_at: datetime | None = None


# ── Ответы админ-операций ────────────────────────────────────────────────────
class IdOut(BaseModel):
    id: int


class CourseAdminOut(CourseSummaryOut):
    is_published: bool


class AssignmentBrief(BaseModel):
    id: int
    type: AssignmentType
    title: str
    max_score: int
    due_at: datetime | None = None


class LessonAdminOut(BaseModel):
    id: int
    title: str
    order_index: int
    theory_md: str | None
    video_url: str | None
    assignments: list[AssignmentBrief]
