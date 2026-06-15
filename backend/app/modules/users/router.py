"""HTTP-эндпоинты домена пользователей: профиль, дети, создание персонала."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.auth.deps import CurrentUser, require_roles
from app.modules.auth.schemas import (
    ChildOut,
    CreateChildIn,
    CreateStaffIn,
    MeOut,
    UpdateChildIn,
)
from app.modules.users import service
from app.modules.users.models import StudentProfile, User

router = APIRouter(tags=["users"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


def _child_out(p: StudentProfile) -> ChildOut:
    return ChildOut(
        user_id=p.user_id,
        nickname=p.nickname,
        birth_date=p.birth_date,
        age_group=p.age_group,
        login_username=p.login_username,
        xp=p.xp,
        streak=p.streak,
    )


@router.get("/users/me", response_model=MeOut)
async def me(user: CurrentUser, db: DbDep):
    return await service.build_me(db, user)


# ── Дети (только родитель, только свои) ──────────────────────────────────────
ParentDep = Annotated[User, Depends(require_roles(UserRole.PARENT))]


@router.post("/children", response_model=ChildOut, status_code=status.HTTP_201_CREATED)
async def create_child(data: CreateChildIn, parent: ParentDep, db: DbDep):
    child = await service.create_child(db, parent, data)
    return _child_out(child)


@router.get("/children", response_model=list[ChildOut])
async def list_children(parent: ParentDep, db: DbDep):
    return [_child_out(c) for c in await service.list_children(db, parent)]


@router.get("/children/{child_id}", response_model=ChildOut)
async def get_child(child_id: int, parent: ParentDep, db: DbDep):
    return _child_out(await service.get_owned_child(db, parent, child_id))


@router.patch("/children/{child_id}", response_model=ChildOut)
async def update_child(child_id: int, data: UpdateChildIn, parent: ParentDep, db: DbDep):
    return _child_out(await service.update_child(db, parent, child_id, data))


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(child_id: int, parent: ParentDep, db: DbDep):
    await service.delete_child(db, parent, child_id)


# ── Создание персонала (только админ) ────────────────────────────────────────
AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN))]


@router.post("/admin/users", response_model=MeOut, status_code=status.HTTP_201_CREATED)
async def create_staff(data: CreateStaffIn, _admin: AdminDep, db: DbDep):
    user = await service.create_staff(db, data)
    return await service.build_me(db, user)
