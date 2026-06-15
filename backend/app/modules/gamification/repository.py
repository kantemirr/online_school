"""Запросы геймификации к БД."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import CodeVerdict, EnrollmentStatus, LessonProgressStatus
from app.modules.catalog import repository as catalog_repo
from app.modules.gamification.models import Achievement, StudentAchievement
from app.modules.grading.models import Submission
from app.modules.learning.models import Enrollment, LessonProgress
from app.modules.users.models import StudentProfile


async def get_profile(db: AsyncSession, student_id: int) -> StudentProfile | None:
    return await db.get(StudentProfile, student_id)


async def list_achievements(db: AsyncSession) -> list[Achievement]:
    return list(await db.scalars(select(Achievement).order_by(Achievement.id)))


async def earned_ids(db: AsyncSession, student_id: int) -> set[int]:
    rows = await db.scalars(
        select(StudentAchievement.achievement_id).where(StudentAchievement.student_id == student_id)
    )
    return set(rows)


async def earned_map(db: AsyncSession, student_id: int) -> dict:
    rows = await db.scalars(
        select(StudentAchievement).where(StudentAchievement.student_id == student_id)
    )
    return {sa.achievement_id: sa.earned_at for sa in rows}


async def nicknames(db: AsyncSession, student_ids: list[int]) -> dict[int, str]:
    if not student_ids:
        return {}
    rows = await db.execute(
        select(StudentProfile.user_id, StudentProfile.nickname).where(
            StudentProfile.user_id.in_(student_ids)
        )
    )
    return {uid: nick for uid, nick in rows.all()}


async def compute_student_stats(db: AsyncSession, student_id: int) -> dict:
    profile = await get_profile(db, student_id)

    # Завершённые уроки ученика (id) через его enrollments
    completed_rows = await db.execute(
        select(LessonProgress.lesson_id)
        .join(Enrollment, Enrollment.id == LessonProgress.enrollment_id)
        .where(
            Enrollment.student_id == student_id,
            LessonProgress.status == LessonProgressStatus.COMPLETED,
        )
    )
    completed_lessons = {lid for (lid,) in completed_rows.all()}

    courses_completed = await db.scalar(
        select(func.count()).select_from(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.status == EnrollmentStatus.COMPLETED,
        )
    ) or 0

    code_passed = await db.scalar(
        select(func.count()).select_from(Submission).where(
            Submission.student_id == student_id,
            Submission.verdict == CodeVerdict.PASSED,
        )
    ) or 0

    # Есть ли полностью пройденный модуль (100% уроков)
    has_perfect_module = False
    enrollments = await db.scalars(
        select(Enrollment).where(Enrollment.student_id == student_id)
    )
    for enrollment in enrollments:
        course = await catalog_repo.get_course_tree(db, enrollment.course_id, only_published=False)
        if course is None:
            continue
        for module in course.modules:
            lesson_ids = {lsn.id for lsn in module.lessons}
            if lesson_ids and lesson_ids <= completed_lessons:
                has_perfect_module = True
                break
        if has_perfect_module:
            break

    return {
        "lessons_completed": len(completed_lessons),
        "courses_completed": courses_completed,
        "code_passed": code_passed,
        "xp": profile.xp if profile else 0,
        "streak": profile.streak if profile else 0,
        "has_perfect_module": has_perfect_module,
    }


# ── Данные для фонового пересчёта ────────────────────────────────────────────
async def all_students_xp(db: AsyncSession) -> list[tuple[int, int]]:
    rows = await db.execute(select(StudentProfile.user_id, StudentProfile.xp))
    return [(uid, xp) for uid, xp in rows.all()]


async def all_enrollment_progress(db: AsyncSession) -> list[tuple[int, int, float]]:
    rows = await db.execute(
        select(Enrollment.course_id, Enrollment.student_id, Enrollment.progress_pct)
    )
    return [(cid, sid, float(pct)) for cid, sid, pct in rows.all()]
