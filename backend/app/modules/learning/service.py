"""Логика прохождения курса: запись, карта, контент урока, завершение, прогресс."""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.db.enums import EnrollmentStatus, LessonProgressStatus
from app.modules.catalog import repository as catalog_repo
from app.modules.catalog.models import Course, Lesson, Module
from app.modules.learning import logic
from app.modules.learning import repository as repo
from app.modules.learning.models import Enrollment, LessonProgress
from app.modules.learning.schemas import (
    AssignmentSummaryOut,
    CoursePassageOut,
    EnrollmentOut,
    LessonContentOut,
    LessonStateOut,
    ModulePassageOut,
    ModuleProgressOut,
    ProgressOut,
)


def _enrollment_out(e: Enrollment) -> EnrollmentOut:
    return EnrollmentOut(
        id=e.id, course_id=e.course_id, status=e.status,
        progress_pct=float(e.progress_pct), enrolled_at=e.enrolled_at,
    )


def _ordered_modules(course: Course) -> list[Module]:
    return sorted(course.modules, key=lambda m: m.order_index)


def _ordered_lessons(course: Course) -> list[Lesson]:
    flat: list[Lesson] = []
    for m in _ordered_modules(course):
        flat.extend(sorted(m.lessons, key=lambda x: x.order_index))
    return flat


def _completed_ids(rows: list[LessonProgress]) -> set[int]:
    return {r.lesson_id for r in rows if r.status == LessonProgressStatus.COMPLETED}


def check_access(student_id: int, course: Course) -> bool:
    """Точка контроля доступа по абонементу (Этап 9). Пока всегда разрешено."""
    return True


# ── Запись ───────────────────────────────────────────────────────────────────
async def enroll(db: AsyncSession, student_id: int, course_id: int) -> EnrollmentOut:
    course = await db.get(Course, course_id)
    if course is None or not course.is_published:
        raise NotFoundError("Курс не найден или не опубликован", code="course_not_found")
    if not check_access(student_id, course):
        raise PermissionDeniedError("Нет активного доступа к курсу", code="no_access")

    existing = await repo.get_enrollment(db, student_id, course_id)
    if existing is not None:
        return _enrollment_out(existing)

    enrollment = Enrollment(student_id=student_id, course_id=course_id, status=EnrollmentStatus.ACTIVE)
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return _enrollment_out(enrollment)


async def list_my_enrollments(db: AsyncSession, student_id: int) -> list[EnrollmentOut]:
    return [_enrollment_out(e) for e in await repo.list_enrollments(db, student_id)]


# ── Карта прохождения ────────────────────────────────────────────────────────
async def _load_context(db: AsyncSession, student_id: int, course_id: int):
    enrollment = await repo.get_enrollment(db, student_id, course_id)
    if enrollment is None:
        raise NotFoundError("Вы не записаны на этот курс", code="not_enrolled")
    course = await catalog_repo.get_course_tree(db, course_id, only_published=False)
    if course is None:
        raise NotFoundError("Курс не найден", code="course_not_found")
    rows = await repo.progress_rows(db, enrollment.id)
    return enrollment, course, rows


async def get_passage(db: AsyncSession, student_id: int, course_id: int) -> CoursePassageOut:
    enrollment, course, rows = await _load_context(db, student_id, course_id)
    status_map = {r.lesson_id: r.status for r in rows}
    completed = _completed_ids(rows)
    ordered_ids = [lsn.id for lsn in _ordered_lessons(course)]
    unlocked = logic.unlocked_lessons(ordered_ids, completed)

    modules_out: list[ModulePassageOut] = []
    for m in _ordered_modules(course):
        lessons_out = [
            LessonStateOut(
                id=lsn.id, title=lsn.title, order_index=lsn.order_index,
                status=status_map.get(lsn.id, LessonProgressStatus.NOT_STARTED),
                locked=lsn.id not in unlocked,
                assignment_count=len(lsn.assignments),
            )
            for lsn in sorted(m.lessons, key=lambda x: x.order_index)
        ]
        modules_out.append(ModulePassageOut(
            id=m.id, title=m.title, order_index=m.order_index, lessons=lessons_out
        ))

    return CoursePassageOut(
        course_id=course.id, title=course.title, status=enrollment.status,
        progress_pct=float(enrollment.progress_pct),
        resume_lesson_id=logic.first_resume_lesson(ordered_ids, completed, unlocked),
        modules=modules_out,
    )


# ── Контент урока (с гейтом доступа) ─────────────────────────────────────────
async def _resolve_course_id(db: AsyncSession, lesson: Lesson) -> int:
    module = await db.get(Module, lesson.module_id)
    return module.course_id


async def ensure_lesson_unlocked(db: AsyncSession, student_id: int, lesson_id: int) -> Enrollment:
    """Проверяет, что ученик записан и урок разблокирован. Возвращает enrollment.

    Переиспользуется грейдингом (Этап 5): доступ к заданию урока.
    """
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise NotFoundError("Урок не найден", code="lesson_not_found")
    course_id = await _resolve_course_id(db, lesson)
    enrollment, course, rows = await _load_context(db, student_id, course_id)
    completed = _completed_ids(rows)
    ordered_ids = [lsn.id for lsn in _ordered_lessons(course)]
    if lesson_id not in logic.unlocked_lessons(ordered_ids, completed):
        raise PermissionDeniedError("Урок ещё заблокирован", code="lesson_locked")
    return enrollment


async def get_lesson_content(
    db: AsyncSession, student_id: int, lesson_id: int
) -> LessonContentOut:
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise NotFoundError("Урок не найден", code="lesson_not_found")
    course_id = await _resolve_course_id(db, lesson)
    enrollment, course, rows = await _load_context(db, student_id, course_id)

    completed = _completed_ids(rows)
    ordered_ids = [lsn.id for lsn in _ordered_lessons(course)]
    unlocked = logic.unlocked_lessons(ordered_ids, completed)
    if lesson_id not in unlocked:
        raise PermissionDeniedError("Урок ещё заблокирован", code="lesson_locked")

    # Берём урок из дерева (с загруженными заданиями)
    lesson_node = next((l for l in _ordered_lessons(course) if l.id == lesson_id), lesson)

    # Отмечаем «в процессе», если ещё не начат
    progress = await repo.get_lesson_progress(db, enrollment.id, lesson_id)
    if progress is None:
        progress = LessonProgress(
            enrollment_id=enrollment.id, lesson_id=lesson_id,
            status=LessonProgressStatus.IN_PROGRESS,
        )
        db.add(progress)
        await db.commit()
    elif progress.status == LessonProgressStatus.NOT_STARTED:
        progress.status = LessonProgressStatus.IN_PROGRESS
        await db.commit()

    return LessonContentOut(
        id=lesson_node.id, title=lesson_node.title,
        theory_md=lesson_node.theory_md, video_url=lesson_node.video_url,
        status=progress.status,
        assignments=[
            AssignmentSummaryOut(id=a.id, type=a.type, title=a.title, max_score=a.max_score)
            for a in lesson_node.assignments
        ],
    )


# ── Завершение урока (переиспользуется грейдингом, Этап 5) ────────────────────
async def mark_lesson_completed(
    db: AsyncSession, enrollment: Enrollment, lesson_id: int, score: int | None = None
) -> None:
    progress = await repo.get_lesson_progress(db, enrollment.id, lesson_id)
    if progress is None:
        progress = LessonProgress(enrollment_id=enrollment.id, lesson_id=lesson_id)
        db.add(progress)
    progress.status = LessonProgressStatus.COMPLETED
    progress.completed_at = datetime.now(timezone.utc)
    if score is not None:
        progress.score = score

    # Пересчёт прогресса курса
    course = await catalog_repo.get_course_tree(db, enrollment.course_id, only_published=False)
    ordered_ids = [lsn.id for lsn in _ordered_lessons(course)]
    rows = await repo.progress_rows(db, enrollment.id)
    completed = _completed_ids(rows) | {lesson_id}
    enrollment.progress_pct = logic.progress_pct(len(ordered_ids), len(completed))
    if ordered_ids and completed >= set(ordered_ids):
        enrollment.status = EnrollmentStatus.COMPLETED
    await db.commit()


async def complete_lesson(
    db: AsyncSession, student_id: int, lesson_id: int, score: int | None = None
) -> CoursePassageOut:
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise NotFoundError("Урок не найден", code="lesson_not_found")
    course_id = await _resolve_course_id(db, lesson)
    enrollment, course, rows = await _load_context(db, student_id, course_id)

    completed = _completed_ids(rows)
    ordered_ids = [lsn.id for lsn in _ordered_lessons(course)]
    unlocked = logic.unlocked_lessons(ordered_ids, completed)
    if lesson_id not in unlocked:
        raise ConflictError("Нельзя завершить заблокированный урок", code="lesson_locked")

    await mark_lesson_completed(db, enrollment, lesson_id, score)
    return await get_passage(db, student_id, course_id)


# ── Числовой прогресс ────────────────────────────────────────────────────────
async def get_progress(db: AsyncSession, student_id: int, course_id: int) -> ProgressOut:
    enrollment, course, rows = await _load_context(db, student_id, course_id)
    completed = _completed_ids(rows)
    ordered_ids = [lsn.id for lsn in _ordered_lessons(course)]
    unlocked = logic.unlocked_lessons(ordered_ids, completed)

    modules_out: list[ModuleProgressOut] = []
    for m in _ordered_modules(course):
        total = len(m.lessons)
        done = sum(1 for lsn in m.lessons if lsn.id in completed)
        modules_out.append(ModuleProgressOut(
            module_id=m.id, title=m.title, completed=done, total=total,
            pct=logic.progress_pct(total, done),
        ))

    return ProgressOut(
        course_id=course.id, status=enrollment.status,
        progress_pct=float(enrollment.progress_pct),
        resume_lesson_id=logic.first_resume_lesson(ordered_ids, completed, unlocked),
        modules=modules_out,
    )
