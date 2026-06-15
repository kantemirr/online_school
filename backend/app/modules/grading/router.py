"""HTTP-эндпоинты заданий, отправок, подсказок и ручной проверки."""
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis
from app.db.enums import UserRole
from app.modules.auth.deps import CurrentUser, require_roles
from app.modules.grading import service
from app.modules.grading.schemas import (
    AssignmentForSolveOut,
    CodeSubmitIn,
    GradingQueueItem,
    HintOut,
    QuizSubmitIn,
    ReviewIn,
    SubmissionOut,
)
from app.modules.users.models import User

router = APIRouter(tags=["grading"])
DbDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]
StudentDep = Annotated[User, Depends(require_roles(UserRole.STUDENT))]
TeacherDep = Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))]


# ── Решение задания ──────────────────────────────────────────────────────────
@router.get("/assignments/{assignment_id}", response_model=AssignmentForSolveOut)
async def get_assignment(assignment_id: int, student: StudentDep, db: DbDep):
    return await service.get_assignment_for_solve(db, student, assignment_id)


@router.post("/assignments/{assignment_id}/submit/quiz", response_model=SubmissionOut)
async def submit_quiz(assignment_id: int, data: QuizSubmitIn, student: StudentDep, db: DbDep):
    return await service.submit_quiz(db, student, assignment_id, data.answers)


@router.post("/assignments/{assignment_id}/submit/code", response_model=SubmissionOut,
             status_code=status.HTTP_202_ACCEPTED)
async def submit_code(assignment_id: int, data: CodeSubmitIn, student: StudentDep, db: DbDep):
    return await service.submit_code(db, student, assignment_id, data.code)


@router.post("/assignments/{assignment_id}/submit/project", response_model=SubmissionOut,
             status_code=status.HTTP_201_CREATED)
async def submit_project(
    assignment_id: int,
    student: StudentDep,
    db: DbDep,
    file: Annotated[UploadFile | None, File()] = None,
    link: Annotated[str | None, Form()] = None,
):
    content = await file.read() if file is not None else None
    filename = file.filename if file is not None else None
    return await service.submit_project(
        db, student, assignment_id, filename=filename, content=content, link=link
    )


# ── Результат и подсказка ────────────────────────────────────────────────────
@router.get("/submissions/{submission_id}", response_model=SubmissionOut)
async def get_submission(submission_id: int, user: CurrentUser, db: DbDep):
    return await service.get_submission(db, user, submission_id)


@router.get("/submissions/{submission_id}/hint", response_model=HintOut)
async def get_hint(submission_id: int, student: StudentDep, db: DbDep, redis: RedisDep):
    return await service.request_hint(db, redis, student, submission_id)


# ── Ручная проверка (преподаватель) ──────────────────────────────────────────
@router.get("/grading/queue", response_model=list[GradingQueueItem])
async def grading_queue(_teacher: TeacherDep, db: DbDep):
    return await service.list_queue(db)


@router.post("/grading/submissions/{submission_id}/review", response_model=SubmissionOut)
async def review(submission_id: int, data: ReviewIn, teacher: TeacherDep, db: DbDep):
    return await service.review_project(db, teacher, submission_id, data)
