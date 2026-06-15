"""Запросы грейдинга к БД."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import SubmissionStatus
from app.modules.catalog.models import Assignment, CodeTest, Question
from app.modules.grading.models import Submission


async def get_assignment(db: AsyncSession, assignment_id: int) -> Assignment | None:
    return await db.get(Assignment, assignment_id)


async def get_questions(db: AsyncSession, assignment_id: int) -> list[Question]:
    rows = await db.scalars(
        select(Question).where(Question.assignment_id == assignment_id).order_by(Question.id)
    )
    return list(rows)


async def get_code_tests(db: AsyncSession, assignment_id: int) -> list[CodeTest]:
    rows = await db.scalars(
        select(CodeTest).where(CodeTest.assignment_id == assignment_id).order_by(CodeTest.id)
    )
    return list(rows)


async def pending_review_queue(db: AsyncSession) -> list[Submission]:
    rows = await db.scalars(
        select(Submission)
        .where(Submission.status == SubmissionStatus.PENDING_REVIEW)
        .order_by(Submission.created_at)
    )
    return list(rows)
