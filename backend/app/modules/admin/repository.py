"""Кросс-доменные запросы админ-панели: пользователи, платежи, группы.

Доменные репозитории отдают данные в разрезе одного пользователя/ресурса;
здесь — общеплатформенные выборки, доступные только администратору.
"""
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import PaymentStatus, UserRole
from app.modules.admin.models import AuditLog
from app.modules.catalog.models import Course
from app.modules.payments.models import Payment, Subscription
from app.modules.scheduling.models import Group, GroupMember, ScheduleSession
from app.modules.users.models import (
    ParentProfile,
    StudentProfile,
    TeacherProfile,
    User,
)

# Отображаемое имя пользователя: у каждой роли — свой профиль (1:1 с users).
_display_name = func.coalesce(
    ParentProfile.full_name, TeacherProfile.full_name, StudentProfile.nickname
)


def _users_base():
    return (
        select(User, _display_name.label("display_name"))
        .outerjoin(ParentProfile, ParentProfile.user_id == User.id)
        .outerjoin(TeacherProfile, TeacherProfile.user_id == User.id)
        .outerjoin(StudentProfile, StudentProfile.user_id == User.id)
    )


async def list_users(
    db: AsyncSession,
    *,
    role: UserRole | None = None,
    is_active: bool | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[tuple[User, str | None]], int]:
    base = _users_base()
    if role is not None:
        base = base.where(User.role == role)
    if is_active is not None:
        base = base.where(User.is_active.is_(is_active))
    if q:
        like = f"%{q}%"
        base = base.where(
            or_(
                User.email.ilike(like),
                ParentProfile.full_name.ilike(like),
                TeacherProfile.full_name.ilike(like),
                StudentProfile.nickname.ilike(like),
            )
        )
    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = await db.execute(
        base.order_by(User.id).offset((page - 1) * size).limit(size)
    )
    return [(u, name) for u, name in rows.all()], total


async def get_user_with_name(
    db: AsyncSession, user_id: int
) -> tuple[User, str | None] | None:
    row = (await db.execute(_users_base().where(User.id == user_id))).first()
    if row is None:
        return None
    return row[0], row[1]


async def count_active_admins(db: AsyncSession) -> int:
    return await db.scalar(
        select(func.count())
        .select_from(User)
        .where(User.role == UserRole.ADMIN, User.is_active.is_(True))
    ) or 0


async def list_payments(
    db: AsyncSession,
    *,
    status: PaymentStatus | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list, int]:
    # parent_id ссылается на parent_profiles.user_id == users.id → join User напрямую.
    base = (
        select(Payment, Subscription.plan, User.email)
        .join(Subscription, Subscription.id == Payment.subscription_id)
        .join(User, User.id == Subscription.parent_id)
    )
    if status is not None:
        base = base.where(Payment.status == status)
    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = await db.execute(
        base.order_by(Payment.id.desc()).offset((page - 1) * size).limit(size)
    )
    return rows.all(), total


async def list_groups(
    db: AsyncSession, *, page: int = 1, size: int = 20
) -> tuple[list, int]:
    members_sq = (
        select(GroupMember.group_id, func.count().label("members"))
        .group_by(GroupMember.group_id)
        .subquery()
    )
    sessions_sq = (
        select(ScheduleSession.group_id, func.count().label("sessions"))
        .group_by(ScheduleSession.group_id)
        .subquery()
    )
    base = (
        select(
            Group,
            TeacherProfile.full_name,
            Course.title,
            func.coalesce(members_sq.c.members, 0),
            func.coalesce(sessions_sq.c.sessions, 0),
        )
        .outerjoin(TeacherProfile, TeacherProfile.user_id == Group.teacher_id)
        .outerjoin(Course, Course.id == Group.course_id)
        .outerjoin(members_sq, members_sq.c.group_id == Group.id)
        .outerjoin(sessions_sq, sessions_sq.c.group_id == Group.id)
    )
    total = await db.scalar(select(func.count()).select_from(Group)) or 0
    rows = await db.execute(
        base.order_by(Group.id).offset((page - 1) * size).limit(size)
    )
    return rows.all(), total


async def list_audit(db: AsyncSession, *, page: int = 1, size: int = 50) -> tuple[list[AuditLog], int]:
    total = await db.scalar(select(func.count()).select_from(AuditLog)) or 0
    rows = await db.scalars(
        select(AuditLog).order_by(AuditLog.id.desc()).offset((page - 1) * size).limit(size)
    )
    return list(rows), total
