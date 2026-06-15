"""Pydantic-схемы аналитики и отчётов."""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


# ── Ученик ───────────────────────────────────────────────────────────────────
class CourseProgressItem(BaseModel):
    course_id: int
    title: str
    progress_pct: float
    status: str
    completed_lessons: int
    avg_score: float


class StudentDashboard(BaseModel):
    xp: int
    streak: int
    rank_global: int | None
    achievements_earned: int
    achievements_total: int
    submissions_total: int
    code_passed: int
    courses: list[CourseProgressItem]


# ── Родитель ─────────────────────────────────────────────────────────────────
class ChildBrief(BaseModel):
    child_id: int
    nickname: str
    xp: int
    streak: int
    courses_enrolled: int
    courses_completed: int
    avg_progress: float


class FamilyExpenses(BaseModel):
    total_spent: Decimal
    payments_count: int
    active_subscriptions: int


class ParentOverview(BaseModel):
    children: list[ChildBrief]
    expenses: FamilyExpenses


class AttendanceSummary(BaseModel):
    present: int
    absent: int
    excused: int
    rate: float  # доля присутствий, %


class AchievementBrief(BaseModel):
    code: str
    title: str
    earned_at: datetime | None


class ChildReport(BaseModel):
    child_id: int
    nickname: str
    xp: int
    streak: int
    courses: list[CourseProgressItem]
    attendance: AttendanceSummary
    achievements: list[AchievementBrief]


# ── Преподаватель ────────────────────────────────────────────────────────────
class GroupStudentRow(BaseModel):
    student_id: int
    nickname: str
    progress_pct: float
    attendance_rate: float
    last_active: date | None


class GroupAnalytics(BaseModel):
    group_id: int
    name: str
    course_id: int
    students: list[GroupStudentRow]
    avg_progress: float
    avg_attendance: float
    active_count: int


# ── Админ ────────────────────────────────────────────────────────────────────
class PopularCourse(BaseModel):
    course_id: int
    title: str
    enrollments: int


class AdminOverview(BaseModel):
    users: dict[str, int]
    enrollments: int
    submissions: int
    active_students_7d: int
    popular_courses: list[PopularCourse]
    revenue_total: Decimal
    payments_count: int


# ── Экспорт отчёта ───────────────────────────────────────────────────────────
class ReportExportOut(BaseModel):
    status: str
    detail: str
