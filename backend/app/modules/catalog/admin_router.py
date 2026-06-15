"""Админ-эндпоинты управления контентом каталога (только роль admin)."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.auth.deps import require_roles
from app.modules.catalog import service
from app.modules.catalog.schemas import (
    AssignmentCreate,
    CourseAdminOut,
    CourseCreate,
    CourseDetailOut,
    CourseUpdate,
    IdOut,
    LessonAdminOut,
    LessonCreate,
    LessonUpdate,
    ModuleCreate,
    ModuleUpdate,
)
from app.modules.catalog.service import _summary  # переиспользуем маппер

router = APIRouter(
    prefix="/admin/catalog",
    tags=["admin:catalog"],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
DbDep = Annotated[AsyncSession, Depends(get_db)]


def _course_admin(c) -> CourseAdminOut:
    return CourseAdminOut(**_summary(c).model_dump(), is_published=c.is_published)


# ── Чтение для редактора (включая неопубликованное) ──────────────────────────
@router.get("/courses", response_model=list[CourseAdminOut])
async def list_admin_courses(db: DbDep):
    return await service.admin_list_courses(db)


@router.get("/courses/{course_id}", response_model=CourseDetailOut)
async def admin_course_detail(course_id: int, db: DbDep):
    return await service.admin_course_detail(db, course_id)


@router.get("/lessons/{lesson_id}", response_model=LessonAdminOut)
async def admin_lesson_detail(lesson_id: int, db: DbDep):
    return await service.admin_lesson_detail(db, lesson_id)


# ── Курсы ────────────────────────────────────────────────────────────────────
@router.post("/courses", response_model=CourseAdminOut, status_code=status.HTTP_201_CREATED)
async def create_course(data: CourseCreate, db: DbDep):
    return _course_admin(await service.create_course(db, data))


@router.patch("/courses/{course_id}", response_model=CourseAdminOut)
async def update_course(course_id: int, data: CourseUpdate, db: DbDep):
    return _course_admin(await service.update_course(db, course_id, data))


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, db: DbDep):
    await service.delete_course(db, course_id)


@router.post("/courses/{course_id}/publish", response_model=CourseAdminOut)
async def publish_course(course_id: int, db: DbDep):
    return _course_admin(await service.set_published(db, course_id, True))


@router.post("/courses/{course_id}/unpublish", response_model=CourseAdminOut)
async def unpublish_course(course_id: int, db: DbDep):
    return _course_admin(await service.set_published(db, course_id, False))


# ── Модули ───────────────────────────────────────────────────────────────────
@router.post("/courses/{course_id}/modules", response_model=IdOut, status_code=status.HTTP_201_CREATED)
async def create_module(course_id: int, data: ModuleCreate, db: DbDep):
    m = await service.create_module(db, course_id, data)
    return IdOut(id=m.id)


@router.patch("/modules/{module_id}", response_model=IdOut)
async def update_module(module_id: int, data: ModuleUpdate, db: DbDep):
    m = await service.update_module(db, module_id, data)
    return IdOut(id=m.id)


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(module_id: int, db: DbDep):
    await service.delete_module(db, module_id)


# ── Уроки ────────────────────────────────────────────────────────────────────
@router.post("/modules/{module_id}/lessons", response_model=IdOut, status_code=status.HTTP_201_CREATED)
async def create_lesson(module_id: int, data: LessonCreate, db: DbDep):
    lsn = await service.create_lesson(db, module_id, data)
    return IdOut(id=lsn.id)


@router.patch("/lessons/{lesson_id}", response_model=IdOut)
async def update_lesson(lesson_id: int, data: LessonUpdate, db: DbDep):
    lsn = await service.update_lesson(db, lesson_id, data)
    return IdOut(id=lsn.id)


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(lesson_id: int, db: DbDep):
    await service.delete_lesson(db, lesson_id)


# ── Задания ──────────────────────────────────────────────────────────────────
@router.post("/lessons/{lesson_id}/assignments", response_model=IdOut, status_code=status.HTTP_201_CREATED)
async def create_assignment(lesson_id: int, data: AssignmentCreate, db: DbDep):
    a = await service.create_assignment(db, lesson_id, data)
    return IdOut(id=a.id)


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(assignment_id: int, db: DbDep):
    await service.delete_assignment(db, assignment_id)
