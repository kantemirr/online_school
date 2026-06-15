"""Pydantic-схемы прохождения и прогресса."""
from datetime import datetime

from pydantic import BaseModel

from app.db.enums import AssignmentType, EnrollmentStatus, LessonProgressStatus


class EnrollmentOut(BaseModel):
    id: int
    course_id: int
    status: EnrollmentStatus
    progress_pct: float
    enrolled_at: datetime


class AssignmentSummaryOut(BaseModel):
    id: int
    type: AssignmentType
    title: str
    max_score: int
    due_at: datetime | None = None


class LessonStateOut(BaseModel):
    id: int
    title: str
    order_index: int
    status: LessonProgressStatus
    locked: bool
    assignment_count: int


class ModulePassageOut(BaseModel):
    id: int
    title: str
    order_index: int
    lessons: list[LessonStateOut]


class CoursePassageOut(BaseModel):
    course_id: int
    title: str
    status: EnrollmentStatus
    progress_pct: float
    resume_lesson_id: int | None
    modules: list[ModulePassageOut]


class LessonContentOut(BaseModel):
    id: int
    title: str
    theory_md: str | None
    video_url: str | None
    status: LessonProgressStatus
    assignments: list[AssignmentSummaryOut]


class ModuleProgressOut(BaseModel):
    module_id: int
    title: str
    completed: int
    total: int
    pct: float


class ProgressOut(BaseModel):
    course_id: int
    status: EnrollmentStatus
    progress_pct: float
    resume_lesson_id: int | None
    modules: list[ModuleProgressOut]
