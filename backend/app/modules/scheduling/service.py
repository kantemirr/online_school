"""Логика групп, расписания и посещаемости."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.db.enums import UserRole
from app.modules.catalog.models import Course
from app.modules.scheduling import repository as repo
from app.modules.scheduling.models import (
    Attendance,
    Group,
    GroupMember,
    ScheduleSession,
)
from app.modules.scheduling.schemas import (
    AddMemberIn,
    AttendanceMarkIn,
    AttendanceRecordOut,
    GroupCreate,
    GroupDetailOut,
    GroupOut,
    MemberOut,
    SessionCreate,
    SessionOut,
    SessionUpdate,
    StudentAttendanceItem,
    StudentGroupOut,
    StudentScheduleItem,
)
from app.modules.users.models import StudentProfile, User


def _session_out(s: ScheduleSession) -> SessionOut:
    return SessionOut(
        id=s.id, group_id=s.group_id, starts_at=s.starts_at,
        ends_at=s.ends_at, meeting_url=s.meeting_url,
    )


async def _owned_group(db: AsyncSession, user: User, group_id: int) -> Group:
    group = await repo.get_group(db, group_id)
    if group is None:
        raise NotFoundError("Группа не найдена", code="group_not_found")
    if user.role != UserRole.ADMIN and group.teacher_id != user.id:
        raise PermissionDeniedError("Это не ваша группа", code="not_group_owner")
    return group


async def _owned_session(db: AsyncSession, user: User, session_id: int) -> ScheduleSession:
    session = await repo.get_session(db, session_id)
    if session is None:
        raise NotFoundError("Занятие не найдено", code="session_not_found")
    await _owned_group(db, user, session.group_id)
    return session


# ── Группы (преподаватель) ───────────────────────────────────────────────────
async def create_group(db: AsyncSession, teacher: User, data: GroupCreate) -> GroupOut:
    if await db.get(Course, data.course_id) is None:
        raise NotFoundError("Курс не найден", code="course_not_found")
    group = Group(course_id=data.course_id, teacher_id=teacher.id, name=data.name)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return GroupOut(id=group.id, course_id=group.course_id, name=group.name,
                    member_count=0, session_count=0)


async def list_my_groups(db: AsyncSession, teacher: User) -> list[GroupOut]:
    result = []
    for group in await repo.teacher_groups(db, teacher.id):
        members, sessions = await repo.counts(db, group.id)
        result.append(GroupOut(id=group.id, course_id=group.course_id, name=group.name,
                               member_count=members, session_count=sessions))
    return result


async def get_group_detail(db: AsyncSession, user: User, group_id: int) -> GroupDetailOut:
    group = await _owned_group(db, user, group_id)
    members = await repo.group_members(db, group_id)
    names = await repo.nicknames(db, [m.student_id for m in members])
    sessions = await repo.group_sessions(db, group_id)
    return GroupDetailOut(
        id=group.id, course_id=group.course_id, name=group.name,
        members=[MemberOut(student_id=m.student_id, nickname=names.get(m.student_id)) for m in members],
        sessions=[_session_out(s) for s in sessions],
    )


async def delete_group(db: AsyncSession, user: User, group_id: int) -> None:
    group = await _owned_group(db, user, group_id)
    await db.delete(group)
    await db.commit()


# ── Состав группы ────────────────────────────────────────────────────────────
async def add_member(db: AsyncSession, user: User, group_id: int, data: AddMemberIn) -> None:
    await _owned_group(db, user, group_id)
    if await db.get(StudentProfile, data.student_id) is None:
        raise NotFoundError("Ученик не найден", code="student_not_found")
    if await repo.is_member(db, group_id, data.student_id):
        raise ConflictError("Ученик уже в группе", code="already_member")
    db.add(GroupMember(group_id=group_id, student_id=data.student_id))
    await db.commit()


async def remove_member(db: AsyncSession, user: User, group_id: int, student_id: int) -> None:
    await _owned_group(db, user, group_id)
    member = await db.get(GroupMember, {"group_id": group_id, "student_id": student_id})
    if member is None:
        raise NotFoundError("Ученик не в группе", code="not_member")
    await db.delete(member)
    await db.commit()


# ── Расписание ───────────────────────────────────────────────────────────────
async def create_session(db: AsyncSession, user: User, group_id: int, data: SessionCreate) -> SessionOut:
    group = await _owned_group(db, user, group_id)
    session = ScheduleSession(
        group_id=group_id, teacher_id=group.teacher_id,
        starts_at=data.starts_at, ends_at=data.ends_at, meeting_url=data.meeting_url,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Уведомления членам группы о новом занятии (+ email родителям)
    from app.modules.notifications import service as notifications
    for member in await repo.group_members(db, group_id):
        await notifications.notify_new_session(db, member.student_id, session)

    return _session_out(session)


async def update_session(db: AsyncSession, user: User, session_id: int, data: SessionUpdate) -> SessionOut:
    session = await _owned_session(db, user, session_id)
    payload = data.model_dump(exclude_unset=True)
    for key, value in payload.items():
        setattr(session, key, value)
    if session.ends_at <= session.starts_at:
        raise ConflictError("Окончание занятия должно быть позже начала", code="bad_times")
    await db.commit()
    await db.refresh(session)
    return _session_out(session)


async def delete_session(db: AsyncSession, user: User, session_id: int) -> None:
    session = await _owned_session(db, user, session_id)
    await db.delete(session)
    await db.commit()


# ── Посещаемость ─────────────────────────────────────────────────────────────
async def mark_attendance(db: AsyncSession, user: User, session_id: int, data: AttendanceMarkIn) -> None:
    session = await _owned_session(db, user, session_id)
    for record in data.records:
        if not await repo.is_member(db, session.group_id, record.student_id):
            raise ConflictError(
                f"Ученик {record.student_id} не состоит в группе занятия", code="not_member"
            )
        existing = await repo.get_attendance(db, session_id, record.student_id)
        if existing is None:
            db.add(Attendance(session_id=session_id, student_id=record.student_id, status=record.status))
        else:
            existing.status = record.status
    await db.commit()


async def get_attendance(db: AsyncSession, user: User, session_id: int) -> list[AttendanceRecordOut]:
    await _owned_session(db, user, session_id)
    rows = await repo.session_attendance(db, session_id)
    names = await repo.nicknames(db, [a.student_id for a in rows])
    return [
        AttendanceRecordOut(student_id=a.student_id, nickname=names.get(a.student_id), status=a.status)
        for a in rows
    ]


# ── Представления ученика ────────────────────────────────────────────────────
async def my_groups(db: AsyncSession, student: User) -> list[StudentGroupOut]:
    return [
        StudentGroupOut(group_id=g.id, name=g.name, course_id=g.course_id)
        for g in await repo.student_groups(db, student.id)
    ]


async def my_schedule(db: AsyncSession, student: User) -> list[StudentScheduleItem]:
    return [
        StudentScheduleItem(
            session_id=s.id, group_id=g.id, group_name=g.name,
            starts_at=s.starts_at, ends_at=s.ends_at, meeting_url=s.meeting_url,
        )
        for s, g in await repo.student_sessions(db, student.id)
    ]


async def my_attendance(db: AsyncSession, student: User) -> list[StudentAttendanceItem]:
    return [
        StudentAttendanceItem(session_id=a.session_id, starts_at=s.starts_at, status=a.status)
        for a, s in await repo.student_attendance(db, student.id)
    ]
