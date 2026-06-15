"""Кросс-модульные агрегаты для аналитики."""
from datetime import date, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import (
    CodeVerdict,
    EnrollmentStatus,
    LessonProgressStatus,
    PaymentStatus,
    SubscriptionStatus,
    UserRole,
)
from app.modules.catalog.models import Course
from app.modules.gamification.models import Achievement, StudentAchievement
from app.modules.grading.models import Submission
from app.modules.learning.models import Enrollment, LessonProgress
from app.modules.payments.models import Payment, Subscription
from app.modules.scheduling.models import Attendance, Group, GroupMember, ScheduleSession
from app.modules.users.models import StudentProfile, User


# ── Ученик / ребёнок ─────────────────────────────────────────────────────────
async def course_progress(db: AsyncSession, student_id: int) -> list[dict]:
    completed = LessonProgressStatus.COMPLETED
    rows = await db.execute(
        select(
            Enrollment.course_id, Course.title, Enrollment.progress_pct, Enrollment.status,
            func.count(LessonProgress.id).filter(LessonProgress.status == completed).label("done"),
            func.coalesce(
                func.avg(case((LessonProgress.status == completed, LessonProgress.score))), 0
            ).label("avg_score"),
        )
        .join(Course, Course.id == Enrollment.course_id)
        .outerjoin(LessonProgress, LessonProgress.enrollment_id == Enrollment.id)
        .where(Enrollment.student_id == student_id)
        .group_by(Enrollment.id, Course.title)
        .order_by(Enrollment.course_id)
    )
    return [
        {"course_id": cid, "title": title, "progress_pct": float(pct), "status": status.value,
         "completed_lessons": done, "avg_score": round(float(avg or 0), 1)}
        for cid, title, pct, status, done, avg in rows.all()
    ]


async def attendance_summary(db: AsyncSession, student_id: int) -> dict:
    rows = await db.execute(
        select(Attendance.status, func.count()).where(Attendance.student_id == student_id)
        .group_by(Attendance.status)
    )
    counts = {status.value: n for status, n in rows.all()}
    present = counts.get("present", 0)
    total = sum(counts.values())
    return {
        "present": present, "absent": counts.get("absent", 0),
        "excused": counts.get("excused", 0),
        "rate": round(present / total * 100, 1) if total else 0.0,
    }


async def submissions_stats(db: AsyncSession, student_id: int) -> dict:
    total = await db.scalar(
        select(func.count()).select_from(Submission).where(Submission.student_id == student_id)
    ) or 0
    passed = await db.scalar(
        select(func.count()).select_from(Submission).where(
            Submission.student_id == student_id, Submission.verdict == CodeVerdict.PASSED
        )
    ) or 0
    return {"total": total, "code_passed": passed}


async def achievements_detail(db: AsyncSession, student_id: int) -> list[dict]:
    rows = await db.execute(
        select(Achievement.code, Achievement.title, StudentAchievement.earned_at)
        .join(StudentAchievement, StudentAchievement.achievement_id == Achievement.id)
        .where(StudentAchievement.student_id == student_id)
        .order_by(StudentAchievement.earned_at)
    )
    return [{"code": c, "title": t, "earned_at": ts} for c, t, ts in rows.all()]


# ── Родитель ─────────────────────────────────────────────────────────────────
async def parent_children(db: AsyncSession, parent_id: int) -> list[StudentProfile]:
    return list(await db.scalars(
        select(StudentProfile).where(StudentProfile.parent_id == parent_id).order_by(StudentProfile.user_id)
    ))


async def child_enrollment_brief(db: AsyncSession, student_id: int) -> dict:
    row = await db.execute(
        select(
            func.count(Enrollment.id),
            func.count(Enrollment.id).filter(Enrollment.status == EnrollmentStatus.COMPLETED),
            func.coalesce(func.avg(Enrollment.progress_pct), 0),
        ).where(Enrollment.student_id == student_id)
    )
    enrolled, completed, avg = row.one()
    return {"courses_enrolled": enrolled, "courses_completed": completed,
            "avg_progress": round(float(avg or 0), 1)}


async def family_expenses(db: AsyncSession, parent_id: int) -> dict:
    paid_sum = await db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .join(Subscription, Subscription.id == Payment.subscription_id)
        .where(Subscription.parent_id == parent_id, Payment.status == PaymentStatus.PAID)
    )
    paid_count = await db.scalar(
        select(func.count(Payment.id))
        .join(Subscription, Subscription.id == Payment.subscription_id)
        .where(Subscription.parent_id == parent_id, Payment.status == PaymentStatus.PAID)
    ) or 0
    active = await db.scalar(
        select(func.count()).select_from(Subscription).where(
            Subscription.parent_id == parent_id, Subscription.status == SubscriptionStatus.ACTIVE
        )
    ) or 0
    return {"total_spent": paid_sum or 0, "payments_count": paid_count, "active_subscriptions": active}


# ── Преподаватель ────────────────────────────────────────────────────────────
async def group_with_members(db: AsyncSession, group_id: int):
    group = await db.get(Group, group_id)
    members = list(await db.scalars(
        select(GroupMember).where(GroupMember.group_id == group_id)
    )) if group else []
    return group, members


async def student_course_progress(db: AsyncSession, student_id: int, course_id: int) -> float:
    pct = await db.scalar(
        select(Enrollment.progress_pct).where(
            Enrollment.student_id == student_id, Enrollment.course_id == course_id
        )
    )
    return float(pct) if pct is not None else 0.0


async def student_group_attendance_rate(db: AsyncSession, student_id: int, group_id: int) -> float:
    total = await db.scalar(
        select(func.count(ScheduleSession.id)).where(ScheduleSession.group_id == group_id)
    ) or 0
    if total == 0:
        return 0.0
    present = await db.scalar(
        select(func.count(Attendance.session_id))
        .join(ScheduleSession, ScheduleSession.id == Attendance.session_id)
        .where(ScheduleSession.group_id == group_id, Attendance.student_id == student_id,
               Attendance.status == "present")
    ) or 0
    return round(present / total * 100, 1)


# ── Админ ────────────────────────────────────────────────────────────────────
async def users_by_role(db: AsyncSession) -> dict[str, int]:
    rows = await db.execute(select(User.role, func.count()).group_by(User.role))
    by_role = {role.value: n for role, n in rows.all()}
    by_role["total"] = sum(by_role.values())
    return by_role


async def platform_counts(db: AsyncSession) -> dict:
    enrollments = await db.scalar(select(func.count()).select_from(Enrollment)) or 0
    submissions = await db.scalar(select(func.count()).select_from(Submission)) or 0
    week_ago = date.today() - timedelta(days=7)
    active = await db.scalar(
        select(func.count()).select_from(StudentProfile).where(
            StudentProfile.last_active_date >= week_ago
        )
    ) or 0
    return {"enrollments": enrollments, "submissions": submissions, "active_students_7d": active}


async def popular_courses(db: AsyncSession, limit: int = 5) -> list[dict]:
    rows = await db.execute(
        select(Course.id, Course.title, func.count(Enrollment.id).label("n"))
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc())
        .limit(limit)
    )
    return [{"course_id": cid, "title": title, "enrollments": n} for cid, title, n in rows.all()]


async def revenue(db: AsyncSession) -> dict:
    total = await db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == PaymentStatus.PAID)
    )
    count = await db.scalar(
        select(func.count()).select_from(Payment).where(Payment.status == PaymentStatus.PAID)
    ) or 0
    return {"revenue_total": total or 0, "payments_count": count}
