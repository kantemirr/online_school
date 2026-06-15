"""HTTP-эндпоинты групп, расписания и посещаемости."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.auth.deps import require_roles
from app.modules.scheduling import service
from app.modules.scheduling.schemas import (
    AddMemberIn,
    AttendanceMarkIn,
    AttendanceRecordOut,
    GroupCreate,
    GroupDetailOut,
    GroupOut,
    SessionCreate,
    SessionOut,
    SessionUpdate,
    StudentAttendanceItem,
    StudentGroupOut,
    StudentScheduleItem,
    StudentSearchOut,
)
from app.modules.users.models import User

router = APIRouter(prefix="/scheduling", tags=["scheduling"])
DbDep = Annotated[AsyncSession, Depends(get_db)]
TeacherDep = Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))]
StudentDep = Annotated[User, Depends(require_roles(UserRole.STUDENT))]


# ── Группы ───────────────────────────────────────────────────────────────────
@router.post("/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
async def create_group(data: GroupCreate, teacher: TeacherDep, db: DbDep):
    return await service.create_group(db, teacher, data)


@router.get("/groups", response_model=list[GroupOut])
async def my_groups(teacher: TeacherDep, db: DbDep):
    return await service.list_my_groups(db, teacher)


@router.get("/students", response_model=list[StudentSearchOut])
async def search_students(teacher: TeacherDep, db: DbDep, q: str | None = None):
    return await service.search_students(db, q)


@router.get("/groups/{group_id}", response_model=GroupDetailOut)
async def group_detail(group_id: int, teacher: TeacherDep, db: DbDep):
    return await service.get_group_detail(db, teacher, group_id)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: int, teacher: TeacherDep, db: DbDep):
    await service.delete_group(db, teacher, group_id)


@router.post("/groups/{group_id}/members", status_code=status.HTTP_204_NO_CONTENT)
async def add_member(group_id: int, data: AddMemberIn, teacher: TeacherDep, db: DbDep):
    await service.add_member(db, teacher, group_id, data)


@router.delete("/groups/{group_id}/members/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: int, student_id: int, teacher: TeacherDep, db: DbDep):
    await service.remove_member(db, teacher, group_id, student_id)


# ── Расписание ───────────────────────────────────────────────────────────────
@router.post("/groups/{group_id}/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
async def create_session(group_id: int, data: SessionCreate, teacher: TeacherDep, db: DbDep):
    return await service.create_session(db, teacher, group_id, data)


@router.patch("/sessions/{session_id}", response_model=SessionOut)
async def update_session(session_id: int, data: SessionUpdate, teacher: TeacherDep, db: DbDep):
    return await service.update_session(db, teacher, session_id, data)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: int, teacher: TeacherDep, db: DbDep):
    await service.delete_session(db, teacher, session_id)


# ── Посещаемость ─────────────────────────────────────────────────────────────
@router.post("/sessions/{session_id}/attendance", status_code=status.HTTP_204_NO_CONTENT)
async def mark_attendance(session_id: int, data: AttendanceMarkIn, teacher: TeacherDep, db: DbDep):
    await service.mark_attendance(db, teacher, session_id, data)


@router.get("/sessions/{session_id}/attendance", response_model=list[AttendanceRecordOut])
async def session_attendance(session_id: int, teacher: TeacherDep, db: DbDep):
    return await service.get_attendance(db, teacher, session_id)


# ── Представления ученика ────────────────────────────────────────────────────
@router.get("/my/groups", response_model=list[StudentGroupOut])
async def student_groups(student: StudentDep, db: DbDep):
    return await service.my_groups(db, student)


@router.get("/my/schedule", response_model=list[StudentScheduleItem])
async def student_schedule(student: StudentDep, db: DbDep):
    return await service.my_schedule(db, student)


@router.get("/my/attendance", response_model=list[StudentAttendanceItem])
async def student_attendance(student: StudentDep, db: DbDep):
    return await service.my_attendance(db, student)
