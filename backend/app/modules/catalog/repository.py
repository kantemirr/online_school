"""Запросы каталога к БД."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.enums import CourseLevel, CourseTrack
from app.modules.catalog.models import Course, Lesson, Module


async def list_courses(
    db: AsyncSession,
    *,
    track: CourseTrack | None = None,
    age: int | None = None,
    level: CourseLevel | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 20,
    only_published: bool = True,
) -> tuple[list[Course], int]:
    conds = []
    if only_published:
        conds.append(Course.is_published.is_(True))
    if track is not None:
        conds.append(Course.track == track)
    if level is not None:
        conds.append(Course.level == level)
    if age is not None:
        conds.append(Course.age_min <= age)
        conds.append(Course.age_max >= age)
    if q:
        conds.append(Course.title.ilike(f"%{q}%"))

    base = select(Course)
    for c in conds:
        base = base.where(c)

    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = await db.scalars(
        base.order_by(Course.id).offset((page - 1) * size).limit(size)
    )
    return list(rows), total


async def get_course_tree(
    db: AsyncSession, course_id: int, *, only_published: bool = True
) -> Course | None:
    stmt = (
        select(Course)
        .where(Course.id == course_id)
        .options(
            selectinload(Course.modules)
            .selectinload(Module.lessons)
            .selectinload(Lesson.assignments)
        )
    )
    if only_published:
        stmt = stmt.where(Course.is_published.is_(True))
    course = await db.scalar(stmt)
    return course


async def track_counts(db: AsyncSession, *, only_published: bool = True) -> dict[str, int]:
    stmt = select(Course.track, func.count(Course.id))
    if only_published:
        stmt = stmt.where(Course.is_published.is_(True))
    stmt = stmt.group_by(Course.track)
    rows = await db.execute(stmt)
    return {track: count for track, count in rows.all()}
