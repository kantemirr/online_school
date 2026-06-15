"""Логика каталога: витрина (с кэшем Redis) и админ-управление контентом."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import cache_get_json, cache_set_json, invalidate_prefix
from app.core.exceptions import NotFoundError
from app.db.enums import CourseLevel, CourseTrack
from app.modules.catalog import repository as repo
from app.modules.catalog.models import (
    Assignment,
    CodeTest,
    Course,
    Lesson,
    Module,
    Question,
)
from app.modules.catalog.schemas import (
    TRACK_LABELS,
    AssignmentBrief,
    AssignmentCreate,
    CourseAdminOut,
    CourseCreate,
    CourseDetailOut,
    CourseListOut,
    CourseSummaryOut,
    LessonAdminOut,
    LessonCreate,
    LessonNodeOut,
    ModuleCreate,
    ModuleNodeOut,
    TrackOut,
)

CACHE_PREFIX = "catalog:"


# ── Мапперы модель → схема ───────────────────────────────────────────────────
def _summary(c: Course) -> CourseSummaryOut:
    return CourseSummaryOut(
        id=c.id, title=c.title, description=c.description, track=c.track,
        age_min=c.age_min, age_max=c.age_max, level=c.level,
        cover_url=c.cover_url, price=c.price,
    )


def _detail(c: Course) -> CourseDetailOut:
    modules = sorted(c.modules, key=lambda m: m.order_index)
    module_nodes: list[ModuleNodeOut] = []
    lesson_total = 0
    for m in modules:
        lessons = sorted(m.lessons, key=lambda x: x.order_index)
        lesson_total += len(lessons)
        module_nodes.append(ModuleNodeOut(
            id=m.id, title=m.title, order_index=m.order_index,
            lessons=[
                LessonNodeOut(
                    id=lsn.id, title=lsn.title, order_index=lsn.order_index,
                    assignment_count=len(lsn.assignments),
                )
                for lsn in lessons
            ],
        ))
    return CourseDetailOut(
        **_summary(c).model_dump(),
        module_count=len(module_nodes),
        lesson_count=lesson_total,
        modules=module_nodes,
    )


# ── Витрина (кэшируется) ─────────────────────────────────────────────────────
async def get_tracks(db: AsyncSession) -> list[TrackOut]:
    key = f"{CACHE_PREFIX}tracks"
    cached = await cache_get_json(key)
    if cached is not None:
        return [TrackOut(**t) for t in cached]

    counts = await repo.track_counts(db)
    result = [
        TrackOut(code=t, label=TRACK_LABELS[t], course_count=int(counts.get(t.value, counts.get(t, 0))))
        for t in CourseTrack
    ]
    await cache_set_json(key, [t.model_dump() for t in result])
    return result


async def list_courses(
    db: AsyncSession, *, track, age, level, q, page, size
) -> CourseListOut:
    key = f"{CACHE_PREFIX}courses:{track}:{age}:{level}:{q}:{page}:{size}"
    cached = await cache_get_json(key)
    if cached is not None:
        return CourseListOut(**cached)

    items, total = await repo.list_courses(
        db, track=track, age=age, level=level, q=q, page=page, size=size
    )
    result = CourseListOut(
        items=[_summary(c) for c in items], total=total, page=page, size=size
    )
    await cache_set_json(key, result.model_dump())
    return result


async def get_course_detail(db: AsyncSession, course_id: int) -> CourseDetailOut:
    key = f"{CACHE_PREFIX}course:{course_id}"
    cached = await cache_get_json(key)
    if cached is not None:
        return CourseDetailOut(**cached)

    course = await repo.get_course_tree(db, course_id, only_published=True)
    if course is None:
        raise NotFoundError("Курс не найден", code="course_not_found")
    result = _detail(course)
    await cache_set_json(key, result.model_dump())
    return result


# ── Админ-чтение (включая неопубликованное, для редактора) ───────────────────
async def admin_list_courses(db: AsyncSession) -> list[CourseAdminOut]:
    items, _ = await repo.list_courses(
        db, track=None, age=None, level=None, q=None, page=1, size=200, only_published=False
    )
    return [CourseAdminOut(**_summary(c).model_dump(), is_published=c.is_published) for c in items]


async def admin_course_detail(db: AsyncSession, course_id: int) -> CourseDetailOut:
    course = await repo.get_course_tree(db, course_id, only_published=False)
    if course is None:
        raise NotFoundError("Курс не найден", code="course_not_found")
    return _detail(course)


async def admin_lesson_detail(db: AsyncSession, lesson_id: int) -> LessonAdminOut:
    lesson = await db.scalar(
        select(Lesson).where(Lesson.id == lesson_id).options(selectinload(Lesson.assignments))
    )
    if lesson is None:
        raise NotFoundError("Урок не найден", code="lesson_not_found")
    return LessonAdminOut(
        id=lesson.id, title=lesson.title, order_index=lesson.order_index,
        theory_md=lesson.theory_md, video_url=lesson.video_url,
        assignments=[
            AssignmentBrief(id=a.id, type=a.type, title=a.title, max_score=a.max_score, due_at=a.due_at)
            for a in sorted(lesson.assignments, key=lambda x: x.id)
        ],
    )


# ── Админ-управление ─────────────────────────────────────────────────────────
async def _next_order(db: AsyncSession, model, fk_field, fk_value) -> int:
    current = await db.scalar(
        select(func.max(getattr(model, "order_index"))).where(getattr(model, fk_field) == fk_value)
    )
    return (current or 0) + 1


async def _get_or_404(db: AsyncSession, model, obj_id: int, name: str):
    obj = await db.get(model, obj_id)
    if obj is None:
        raise NotFoundError(f"{name} не найден", code="not_found")
    return obj


async def create_course(db: AsyncSession, data: CourseCreate) -> Course:
    course = Course(**data.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    await invalidate_prefix(CACHE_PREFIX)
    return course


async def update_course(db: AsyncSession, course_id: int, data) -> Course:
    course = await _get_or_404(db, Course, course_id, "Курс")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(course, k, v)
    await db.commit()
    await db.refresh(course)
    await invalidate_prefix(CACHE_PREFIX)
    return course


async def delete_course(db: AsyncSession, course_id: int) -> None:
    course = await _get_or_404(db, Course, course_id, "Курс")
    await db.delete(course)
    await db.commit()
    await invalidate_prefix(CACHE_PREFIX)


async def set_published(db: AsyncSession, course_id: int, published: bool) -> Course:
    course = await _get_or_404(db, Course, course_id, "Курс")
    course.is_published = published
    await db.commit()
    await db.refresh(course)
    await invalidate_prefix(CACHE_PREFIX)
    return course


async def create_module(db: AsyncSession, course_id: int, data: ModuleCreate) -> Module:
    await _get_or_404(db, Course, course_id, "Курс")
    order = data.order_index if data.order_index is not None else await _next_order(db, Module, "course_id", course_id)
    module = Module(course_id=course_id, title=data.title, order_index=order)
    db.add(module)
    await db.commit()
    await db.refresh(module)
    await invalidate_prefix(CACHE_PREFIX)
    return module


async def update_module(db: AsyncSession, module_id: int, data) -> Module:
    module = await _get_or_404(db, Module, module_id, "Модуль")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(module, k, v)
    await db.commit()
    await db.refresh(module)
    await invalidate_prefix(CACHE_PREFIX)
    return module


async def delete_module(db: AsyncSession, module_id: int) -> None:
    module = await _get_or_404(db, Module, module_id, "Модуль")
    await db.delete(module)
    await db.commit()
    await invalidate_prefix(CACHE_PREFIX)


async def create_lesson(db: AsyncSession, module_id: int, data: LessonCreate) -> Lesson:
    await _get_or_404(db, Module, module_id, "Модуль")
    order = data.order_index if data.order_index is not None else await _next_order(db, Lesson, "module_id", module_id)
    lesson = Lesson(
        module_id=module_id, title=data.title, order_index=order,
        theory_md=data.theory_md, video_url=data.video_url,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    await invalidate_prefix(CACHE_PREFIX)
    return lesson


async def update_lesson(db: AsyncSession, lesson_id: int, data) -> Lesson:
    lesson = await _get_or_404(db, Lesson, lesson_id, "Урок")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(lesson, k, v)
    await db.commit()
    await db.refresh(lesson)
    await invalidate_prefix(CACHE_PREFIX)
    return lesson


async def delete_lesson(db: AsyncSession, lesson_id: int) -> None:
    lesson = await _get_or_404(db, Lesson, lesson_id, "Урок")
    await db.delete(lesson)
    await db.commit()
    await invalidate_prefix(CACHE_PREFIX)


async def create_assignment(db: AsyncSession, lesson_id: int, data: AssignmentCreate) -> Assignment:
    await _get_or_404(db, Lesson, lesson_id, "Урок")
    assignment = Assignment(
        lesson_id=lesson_id, type=data.type, title=data.title,
        max_score=data.max_score, due_at=data.due_at,
    )
    for qd in data.questions:
        assignment.questions.append(Question(**qd.model_dump()))
    for td in data.code_tests:
        assignment.code_tests.append(CodeTest(**td.model_dump()))
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    await invalidate_prefix(CACHE_PREFIX)
    return assignment


async def delete_assignment(db: AsyncSession, assignment_id: int) -> None:
    assignment = await _get_or_404(db, Assignment, assignment_id, "Задание")
    await db.delete(assignment)
    await db.commit()
    await invalidate_prefix(CACHE_PREFIX)
