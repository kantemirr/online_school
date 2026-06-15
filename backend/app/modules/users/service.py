"""Прикладная логика домена пользователей: профиль, дети, создание персонала."""
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password, hash_pin
from app.db.enums import UserRole
from app.modules.auth.schemas import (
    CreateChildIn,
    CreateStaffIn,
    MeOut,
    UpdateChildIn,
)
from app.modules.users.models import (
    ParentProfile,
    StudentProfile,
    TeacherProfile,
    User,
)
from app.modules.users.utils import age_group_for


async def build_me(db: AsyncSession, user: User) -> MeOut:
    display_name: str | None = None
    if user.role == UserRole.PARENT:
        p = await db.get(ParentProfile, user.id)
        display_name = p.full_name if p else None
    elif user.role == UserRole.TEACHER:
        t = await db.get(TeacherProfile, user.id)
        display_name = t.full_name if t else None
    elif user.role == UserRole.STUDENT:
        s = await db.get(StudentProfile, user.id)
        display_name = s.nickname if s else None
    return MeOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        display_name=display_name,
    )


# ── Дети ─────────────────────────────────────────────────────────────────────
async def _ensure_username_free(db: AsyncSession, login_username: str) -> None:
    taken = await db.scalar(
        select(StudentProfile).where(StudentProfile.login_username == login_username)
    )
    if taken is not None:
        raise ConflictError("Логин ребёнка уже занят", code="username_taken")


async def create_child(db: AsyncSession, parent: User, data: CreateChildIn) -> StudentProfile:
    await _ensure_username_free(db, data.login_username)
    # У ребёнка нет email и пароля — вход по PIN. password_hash непригоден для входа.
    child = User(
        email=None,
        password_hash=hash_password(secrets.token_urlsafe(16)),
        role=UserRole.STUDENT,
        is_active=True,
        is_email_verified=False,
    )
    child.student_profile = StudentProfile(
        parent_id=parent.id,
        nickname=data.nickname,
        birth_date=data.birth_date,
        age_group=age_group_for(data.birth_date),
        login_username=data.login_username,
        pin_hash=hash_pin(data.pin),
    )
    db.add(child)
    await db.commit()
    await db.refresh(child.student_profile)
    return child.student_profile


async def list_children(db: AsyncSession, parent: User) -> list[StudentProfile]:
    rows = await db.scalars(
        select(StudentProfile).where(StudentProfile.parent_id == parent.id)
    )
    return list(rows)


async def get_owned_child(db: AsyncSession, parent: User, child_id: int) -> StudentProfile:
    child = await db.get(StudentProfile, child_id)
    if child is None or child.parent_id != parent.id:
        raise NotFoundError("Профиль ребёнка не найден", code="child_not_found")
    return child


async def update_child(
    db: AsyncSession, parent: User, child_id: int, data: UpdateChildIn
) -> StudentProfile:
    child = await get_owned_child(db, parent, child_id)
    if data.nickname is not None:
        child.nickname = data.nickname
    if data.pin is not None:
        child.pin_hash = hash_pin(data.pin)
    await db.commit()
    await db.refresh(child)
    return child


async def delete_child(db: AsyncSession, parent: User, child_id: int) -> None:
    child = await get_owned_child(db, parent, child_id)
    user = await db.get(User, child.user_id)
    await db.delete(user)  # каскад удалит профиль
    await db.commit()


# ── Создание персонала администратором ───────────────────────────────────────
async def create_staff(db: AsyncSession, actor: User, data: CreateStaffIn) -> User:
    exists = await db.scalar(select(User).where(User.email == data.email))
    if exists is not None:
        raise ConflictError("Пользователь с таким email уже существует", code="email_taken")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        is_active=True,
        is_email_verified=True,
    )
    if data.role == UserRole.TEACHER:
        user.teacher_profile = TeacherProfile(
            full_name=data.full_name, specialization=data.specialization
        )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    from app.modules.admin.audit import record_audit
    await record_audit(db, actor, "staff_create", target=f"user#{user.id}", meta={"role": data.role.value})
    return user
