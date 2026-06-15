"""Запросы групп, расписания и посещаемости."""
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.scheduling.models import (
    Attendance,
    Group,
    GroupMember,
    ScheduleSession,
)
from app.modules.users.models import StudentProfile


async def get_group(db: AsyncSession, group_id: int) -> Group | None:
    return await db.get(Group, group_id)


async def get_session(db: AsyncSession, session_id: int) -> ScheduleSession | None:
    return await db.get(ScheduleSession, session_id)


async def teacher_groups(db: AsyncSession, teacher_id: int) -> list[Group]:
    return list(await db.scalars(
        select(Group).where(Group.teacher_id == teacher_id).order_by(Group.id)
    ))


async def group_members(db: AsyncSession, group_id: int) -> list[GroupMember]:
    return list(await db.scalars(
        select(GroupMember).where(GroupMember.group_id == group_id)
    ))


async def group_sessions(db: AsyncSession, group_id: int) -> list[ScheduleSession]:
    return list(await db.scalars(
        select(ScheduleSession).where(ScheduleSession.group_id == group_id)
        .order_by(ScheduleSession.starts_at)
    ))


async def is_member(db: AsyncSession, group_id: int, student_id: int) -> bool:
    found = await db.scalar(
        select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.student_id == student_id
        )
    )
    return found is not None


async def counts(db: AsyncSession, group_id: int) -> tuple[int, int]:
    members = await db.scalar(
        select(func.count()).select_from(GroupMember).where(GroupMember.group_id == group_id)
    ) or 0
    sessions = await db.scalar(
        select(func.count()).select_from(ScheduleSession).where(ScheduleSession.group_id == group_id)
    ) or 0
    return members, sessions


async def session_attendance(db: AsyncSession, session_id: int) -> list[Attendance]:
    return list(await db.scalars(
        select(Attendance).where(Attendance.session_id == session_id)
    ))


async def get_attendance(db: AsyncSession, session_id: int, student_id: int) -> Attendance | None:
    return await db.scalar(
        select(Attendance).where(
            Attendance.session_id == session_id, Attendance.student_id == student_id
        )
    )


async def search_students(db: AsyncSession, q: str | None, limit: int = 20) -> list[StudentProfile]:
    stmt = select(StudentProfile).order_by(StudentProfile.nickname).limit(limit)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(StudentProfile.nickname.ilike(like), StudentProfile.login_username.ilike(like))
        )
    return list(await db.scalars(stmt))


async def nicknames(db: AsyncSession, student_ids: list[int]) -> dict[int, str]:
    if not student_ids:
        return {}
    rows = await db.execute(
        select(StudentProfile.user_id, StudentProfile.nickname).where(
            StudentProfile.user_id.in_(student_ids)
        )
    )
    return {uid: nick for uid, nick in rows.all()}


# ── Представления ученика ────────────────────────────────────────────────────
async def student_group_ids(db: AsyncSession, student_id: int) -> list[int]:
    rows = await db.scalars(
        select(GroupMember.group_id).where(GroupMember.student_id == student_id)
    )
    return list(rows)


async def student_groups(db: AsyncSession, student_id: int) -> list[Group]:
    return list(await db.scalars(
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.student_id == student_id)
        .order_by(Group.id)
    ))


async def student_sessions(db: AsyncSession, student_id: int) -> list[tuple[ScheduleSession, Group]]:
    rows = await db.execute(
        select(ScheduleSession, Group)
        .join(Group, Group.id == ScheduleSession.group_id)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.student_id == student_id)
        .order_by(ScheduleSession.starts_at)
    )
    return [(s, g) for s, g in rows.all()]


async def student_attendance(db: AsyncSession, student_id: int) -> list[tuple[Attendance, ScheduleSession]]:
    rows = await db.execute(
        select(Attendance, ScheduleSession)
        .join(ScheduleSession, ScheduleSession.id == Attendance.session_id)
        .where(Attendance.student_id == student_id)
        .order_by(ScheduleSession.starts_at)
    )
    return [(a, s) for a, s in rows.all()]
