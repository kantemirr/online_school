"""Публичные эндпоинты каталога (чтение витрины, без авторизации)."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import CourseLevel, CourseTrack
from app.modules.catalog import service
from app.modules.catalog.schemas import CourseDetailOut, CourseListOut, TrackOut

router = APIRouter(prefix="/catalog", tags=["catalog"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/tracks", response_model=list[TrackOut])
async def list_tracks(db: DbDep):
    return await service.get_tracks(db)


@router.get("/courses", response_model=CourseListOut)
async def list_courses(
    db: DbDep,
    track: CourseTrack | None = None,
    age: int | None = Query(default=None, ge=4, le=18),
    level: CourseLevel | None = None,
    q: str | None = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    return await service.list_courses(db, track=track, age=age, level=level, q=q, page=page, size=size)


@router.get("/courses/{course_id}", response_model=CourseDetailOut)
async def get_course(course_id: int, db: DbDep):
    return await service.get_course_detail(db, course_id)
