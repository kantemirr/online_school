"""Демо-аккаунты и наполнение для показа и скриншотов ВКР (идемпотентно).

Запуск: `python -m app.db.seeds_demo`

Фиксированные учётные записи с известными паролями:
  родитель       parent@codekids.ru  / parent12345
  ребёнок        логин kid / PIN 1234   (вход на странице «Вход для ребёнка»)
  преподаватель  teacher@codekids.ru / teacher12345

Плюс: запись ребёнка на бесплатный демо-курс, группа преподавателя с ребёнком и
одно будущее занятие — чтобы экраны всех ролей были населены данными.
"""
import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password, hash_pin
from app.db.enums import EnrollmentStatus, UserRole
from app.db.session import SessionLocal
from app.modules.catalog.models import Course
from app.modules.learning.models import Enrollment
from app.modules.scheduling.models import Group, GroupMember, ScheduleSession
from app.modules.users.models import ParentProfile, StudentProfile, TeacherProfile, User
from app.modules.users.utils import age_group_for

PARENT_EMAIL = "parent@codekids.ru"
TEACHER_EMAIL = "teacher@codekids.ru"
CHILD_LOGIN = "kid"
GROUP_NAME = "Демо-группа Python"
DEMO_COURSE_TITLE = "Python с нуля для детей"


async def _user_id_by_email(db, email: str) -> int:
    return await db.scalar(select(User.id).where(User.email == email))


async def seed_demo() -> None:
    async with SessionLocal() as db:
        # ── Родитель ─────────────────────────────────────────────────────────
        parent_id = await _user_id_by_email(db, PARENT_EMAIL)
        if parent_id is None:
            user = User(
                email=PARENT_EMAIL,
                password_hash=hash_password("parent12345"),
                role=UserRole.PARENT,
                is_active=True,
                is_email_verified=True,
            )
            user.parent_profile = ParentProfile(full_name="Родитель Демидов", consent_pdn=True)
            db.add(user)
            await db.commit()
            parent_id = await _user_id_by_email(db, PARENT_EMAIL)

        # ── Ребёнок ──────────────────────────────────────────────────────────
        child_id = await db.scalar(
            select(StudentProfile.user_id).where(StudentProfile.login_username == CHILD_LOGIN)
        )
        if child_id is None:
            bday = date(2014, 5, 1)
            user = User(
                email=None,
                password_hash=hash_password("disabled"),
                role=UserRole.STUDENT,
                is_active=True,
                is_email_verified=False,
            )
            user.student_profile = StudentProfile(
                parent_id=parent_id,
                nickname="Алиса",
                birth_date=bday,
                age_group=age_group_for(bday),
                login_username=CHILD_LOGIN,
                pin_hash=hash_pin("1234"),
            )
            db.add(user)
            await db.commit()
            child_id = await db.scalar(
                select(StudentProfile.user_id).where(StudentProfile.login_username == CHILD_LOGIN)
            )

        # ── Преподаватель ────────────────────────────────────────────────────
        teacher_id = await _user_id_by_email(db, TEACHER_EMAIL)
        if teacher_id is None:
            user = User(
                email=TEACHER_EMAIL,
                password_hash=hash_password("teacher12345"),
                role=UserRole.TEACHER,
                is_active=True,
                is_email_verified=True,
            )
            user.teacher_profile = TeacherProfile(full_name="Преподаватель Иванова", specialization="Python")
            db.add(user)
            await db.commit()
            teacher_id = await _user_id_by_email(db, TEACHER_EMAIL)

        # ── Наполнение (если демо-курс существует) ───────────────────────────
        course_id = await db.scalar(select(Course.id).where(Course.title == DEMO_COURSE_TITLE))
        if course_id is not None:
            enrolled = await db.scalar(
                select(Enrollment.id).where(
                    Enrollment.student_id == child_id, Enrollment.course_id == course_id
                )
            )
            if enrolled is None:
                db.add(Enrollment(student_id=child_id, course_id=course_id, status=EnrollmentStatus.ACTIVE))
                await db.commit()

            group_id = await db.scalar(select(Group.id).where(Group.name == GROUP_NAME))
            if group_id is None:
                group = Group(course_id=course_id, teacher_id=teacher_id, name=GROUP_NAME)
                db.add(group)
                await db.commit()
                group_id = await db.scalar(select(Group.id).where(Group.name == GROUP_NAME))
                db.add(GroupMember(group_id=group_id, student_id=child_id))
                start = datetime.now(timezone.utc) + timedelta(days=2, hours=1)
                db.add(
                    ScheduleSession(
                        group_id=group_id,
                        teacher_id=teacher_id,
                        starts_at=start,
                        ends_at=start + timedelta(hours=1),
                        meeting_url="https://meet.jit.si/codekids-demo",
                    )
                )
                await db.commit()

        print(
            "demo accounts ready:\n"
            "  parent@codekids.ru / parent12345\n"
            "  teacher@codekids.ru / teacher12345\n"
            "  child login 'kid' / PIN 1234"
        )


if __name__ == "__main__":
    asyncio.run(seed_demo())
