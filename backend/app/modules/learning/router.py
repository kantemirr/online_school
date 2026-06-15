"""HTTP-эндпоинты прохождения курса (роль student, только свои данные)."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.auth.deps import require_roles
from app.modules.learning import service
from app.modules.learning.schemas import (
    CoursePassageOut,
    EnrollmentOut,
    LessonContentOut,
    ProgressOut,
)
from app.modules.users.models import User

router = APIRouter(prefix="/learning", tags=["learning"])
DbDep = Annotated[AsyncSession, Depends(get_db)]
StudentDep = Annotated[User, Depends(require_roles(UserRole.STUDENT))]


@router.post("/courses/{course_id}/enroll", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED)
async def enroll(course_id: int, student: StudentDep, db: DbDep):
    return await service.enroll(db, student.id, course_id)


@router.get("/enrollments", response_model=list[EnrollmentOut])
async def my_enrollments(student: StudentDep, db: DbDep):
    return await service.list_my_enrollments(db, student.id)


@router.get("/courses/{course_id}", response_model=CoursePassageOut)
async def course_passage(course_id: int, student: StudentDep, db: DbDep):
    return await service.get_passage(db, student.id, course_id)


@router.get("/courses/{course_id}/progress", response_model=ProgressOut)
async def course_progress(course_id: int, student: StudentDep, db: DbDep):
    return await service.get_progress(db, student.id, course_id)


@router.get("/lessons/{lesson_id}", response_model=LessonContentOut)
async def lesson_content(lesson_id: int, student: StudentDep, db: DbDep):
    return await service.get_lesson_content(db, student.id, lesson_id)


@router.post("/lessons/{lesson_id}/complete", response_model=CoursePassageOut)
async def complete_lesson(lesson_id: int, student: StudentDep, db: DbDep):
    return await service.complete_lesson(db, student.id, lesson_id)
