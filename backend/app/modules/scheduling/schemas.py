"""Pydantic-схемы групп, расписания и посещаемости."""
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.db.enums import AttendanceStatus


# ── Группы ───────────────────────────────────────────────────────────────────
class GroupCreate(BaseModel):
    course_id: int
    name: str = Field(min_length=1, max_length=255)


class MemberOut(BaseModel):
    student_id: int
    nickname: str | None


class GroupOut(BaseModel):
    id: int
    course_id: int
    name: str
    member_count: int
    session_count: int


class SessionOut(BaseModel):
    id: int
    group_id: int
    starts_at: datetime
    ends_at: datetime
    meeting_url: str | None


class GroupDetailOut(BaseModel):
    id: int
    course_id: int
    name: str
    members: list[MemberOut]
    sessions: list[SessionOut]


class AddMemberIn(BaseModel):
    student_id: int


class StudentSearchOut(BaseModel):
    student_id: int
    nickname: str
    login_username: str | None


# ── Расписание ───────────────────────────────────────────────────────────────
class SessionCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime
    meeting_url: str | None = Field(default=None, max_length=512)

    @model_validator(mode="after")
    def _check_times(self) -> "SessionCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("Окончание занятия должно быть позже начала")
        return self


class SessionUpdate(BaseModel):
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    meeting_url: str | None = Field(default=None, max_length=512)


# ── Посещаемость ─────────────────────────────────────────────────────────────
class AttendanceRecordIn(BaseModel):
    student_id: int
    status: AttendanceStatus


class AttendanceMarkIn(BaseModel):
    records: list[AttendanceRecordIn]


class AttendanceRecordOut(BaseModel):
    student_id: int
    nickname: str | None
    status: AttendanceStatus


# ── Представления ученика ────────────────────────────────────────────────────
class StudentGroupOut(BaseModel):
    group_id: int
    name: str
    course_id: int


class StudentScheduleItem(BaseModel):
    session_id: int
    group_id: int
    group_name: str
    starts_at: datetime
    ends_at: datetime
    meeting_url: str | None


class StudentAttendanceItem(BaseModel):
    session_id: int
    starts_at: datetime
    status: AttendanceStatus
