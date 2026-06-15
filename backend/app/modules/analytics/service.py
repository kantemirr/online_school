"""Логика аналитики: сборка дашбордов по ролям + экспорт отчёта."""
from app.core.cache import cache_get_json, cache_set_json
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.queue import enqueue
from app.db.enums import UserRole
from app.modules.analytics import repository as repo
from app.modules.analytics.schemas import (
    AchievementBrief,
    AdminOverview,
    AttendanceSummary,
    ChildBrief,
    ChildReport,
    CourseProgressItem,
    FamilyExpenses,
    GroupAnalytics,
    GroupStudentRow,
    ParentOverview,
    PopularCourse,
    ReportExportOut,
    StudentDashboard,
)
from app.modules.gamification import leaderboard
from app.modules.gamification import repository as gam_repo
from app.modules.users.models import StudentProfile, User
from sqlalchemy.ext.asyncio import AsyncSession

_ADMIN_CACHE_KEY = "analytics:admin:overview"


def safe_pct(part: float, total: float) -> float:
    return round(part / total * 100, 1) if total else 0.0


def _courses(rows: list[dict]) -> list[CourseProgressItem]:
    return [CourseProgressItem(**r) for r in rows]


# ── Ученик ───────────────────────────────────────────────────────────────────
async def student_dashboard(db: AsyncSession, student: User) -> StudentDashboard:
    profile = await gam_repo.get_profile(db, student.id)
    earned = await gam_repo.earned_ids(db, student.id)
    total = len(await gam_repo.list_achievements(db))
    subs = await repo.submissions_stats(db, student.id)
    return StudentDashboard(
        xp=profile.xp if profile else 0,
        streak=profile.streak if profile else 0,
        rank_global=await leaderboard.rank(leaderboard.GLOBAL_KEY, student.id),
        achievements_earned=len(earned), achievements_total=total,
        submissions_total=subs["total"], code_passed=subs["code_passed"],
        courses=_courses(await repo.course_progress(db, student.id)),
    )


# ── Родитель ─────────────────────────────────────────────────────────────────
async def parent_overview(db: AsyncSession, parent: User) -> ParentOverview:
    children = []
    for profile in await repo.parent_children(db, parent.id):
        brief = await repo.child_enrollment_brief(db, profile.user_id)
        children.append(ChildBrief(
            child_id=profile.user_id, nickname=profile.nickname,
            xp=profile.xp, streak=profile.streak, **brief,
        ))
    exp = await repo.family_expenses(db, parent.id)
    return ParentOverview(children=children, expenses=FamilyExpenses(**exp))


async def _owned_child(db: AsyncSession, parent: User, child_id: int) -> StudentProfile:
    child = await db.get(StudentProfile, child_id)
    if child is None or child.parent_id != parent.id:
        raise NotFoundError("Профиль ребёнка не найден", code="child_not_found")
    return child


async def child_report(db: AsyncSession, parent: User, child_id: int) -> ChildReport:
    child = await _owned_child(db, parent, child_id)
    return ChildReport(
        child_id=child.user_id, nickname=child.nickname, xp=child.xp, streak=child.streak,
        courses=_courses(await repo.course_progress(db, child_id)),
        attendance=AttendanceSummary(**await repo.attendance_summary(db, child_id)),
        achievements=[AchievementBrief(**a) for a in await repo.achievements_detail(db, child_id)],
    )


async def export_report(db: AsyncSession, parent: User, child_id: int) -> ReportExportOut:
    await _owned_child(db, parent, child_id)
    await enqueue("generate_report", child_id)
    return ReportExportOut(status="queued", detail="Отчёт формируется, файл появится в загрузках.")


async def render_report(db: AsyncSession, parent: User, child_id: int) -> str:
    """HTML-отчёт об успеваемости ребёнка для немедленного просмотра/печати."""
    await _owned_child(db, parent, child_id)
    from app.modules.analytics.report import build_report_html

    html = await build_report_html(db, child_id)
    if html is None:
        raise NotFoundError("Профиль ребёнка не найден", code="child_not_found")
    return html


# ── Преподаватель ────────────────────────────────────────────────────────────
async def group_analytics(db: AsyncSession, user: User, group_id: int) -> GroupAnalytics:
    group, members = await repo.group_with_members(db, group_id)
    if group is None:
        raise NotFoundError("Группа не найдена", code="group_not_found")
    if user.role != UserRole.ADMIN and group.teacher_id != user.id:
        raise PermissionDeniedError("Это не ваша группа", code="not_group_owner")

    rows: list[GroupStudentRow] = []
    for member in members:
        profile = await db.get(StudentProfile, member.student_id)
        progress = await repo.student_course_progress(db, member.student_id, group.course_id)
        attendance = await repo.student_group_attendance_rate(db, member.student_id, group_id)
        rows.append(GroupStudentRow(
            student_id=member.student_id,
            nickname=profile.nickname if profile else None,
            progress_pct=progress, attendance_rate=attendance,
            last_active=profile.last_active_date if profile else None,
        ))

    n = len(rows)
    return GroupAnalytics(
        group_id=group.id, name=group.name, course_id=group.course_id, students=rows,
        avg_progress=round(sum(r.progress_pct for r in rows) / n, 1) if n else 0.0,
        avg_attendance=round(sum(r.attendance_rate for r in rows) / n, 1) if n else 0.0,
        active_count=sum(1 for r in rows if r.progress_pct > 0),
    )


# ── Админ (кэш) ──────────────────────────────────────────────────────────────
async def admin_overview(db: AsyncSession) -> AdminOverview:
    cached = await cache_get_json(_ADMIN_CACHE_KEY)
    if cached is not None:
        return AdminOverview(**cached)

    counts = await repo.platform_counts(db)
    rev = await repo.revenue(db)
    overview = AdminOverview(
        users=await repo.users_by_role(db),
        enrollments=counts["enrollments"], submissions=counts["submissions"],
        active_students_7d=counts["active_students_7d"],
        popular_courses=[PopularCourse(**c) for c in await repo.popular_courses(db)],
        revenue_total=rev["revenue_total"], payments_count=rev["payments_count"],
    )
    await cache_set_json(_ADMIN_CACHE_KEY, overview.model_dump(), ttl=60)
    return overview
