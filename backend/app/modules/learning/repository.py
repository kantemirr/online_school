"""Запросы прохождения к БД."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.learning.models import Enrollment, LessonProgress


async def get_enrollment(
    db: AsyncSession, student_id: int, course_id: int
) -> Enrollment | None:
    return await db.scalar(
        select(Enrollment).where(
            Enrollment.student_id == student_id, Enrollment.course_id == course_id
        )
    )


async def list_enrollments(db: AsyncSession, student_id: int) -> list[Enrollment]:
    rows = await db.scalars(
        select(Enrollment).where(Enrollment.student_id == student_id).order_by(Enrollment.id)
    )
    return list(rows)


async def progress_rows(db: AsyncSession, enrollment_id: int) -> list[LessonProgress]:
    rows = await db.scalars(
        select(LessonProgress).where(LessonProgress.enrollment_id == enrollment_id)
    )
    return list(rows)


async def get_lesson_progress(
    db: AsyncSession, enrollment_id: int, lesson_id: int
) -> LessonProgress | None:
    return await db.scalar(
        select(LessonProgress).where(
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.lesson_id == lesson_id,
        )
    )
