"""HTTP-эндпоинты админ-панели: пользователи, реестры, справочники.

Весь префикс `/admin` закрыт ролью администратора. Дополняет существующие
админ-поверхности: `/admin/users` (POST — создание персонала, модуль users),
`/admin/catalog/*` (контент) и `/analytics/admin/overview` (метрики).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import PaymentStatus, UserRole
from app.modules.admin import service
from app.modules.admin.schemas import (
    AdminAuditListOut,
    AdminGroupListOut,
    AdminPaymentListOut,
    AdminUserListOut,
    AdminUserOut,
    ReferenceOut,
    ResetPasswordIn,
    UpdateUserIn,
)
from app.modules.auth.deps import CurrentUser, require_roles

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
DbDep = Annotated[AsyncSession, Depends(get_db)]


# ── Пользователи ─────────────────────────────────────────────────────────────
@router.get("/users", response_model=AdminUserListOut)
async def list_users(
    db: DbDep,
    role: UserRole | None = None,
    is_active: bool | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return await service.list_users(
        db, role=role, is_active=is_active, q=q, page=page, size=size
    )


@router.get("/users/{user_id}", response_model=AdminUserOut)
async def get_user(user_id: int, db: DbDep):
    return await service.get_user(db, user_id)


@router.patch("/users/{user_id}", response_model=AdminUserOut)
async def update_user(user_id: int, data: UpdateUserIn, admin: CurrentUser, db: DbDep):
    return await service.update_user(db, admin, user_id, data)


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(user_id: int, data: ResetPasswordIn, admin: CurrentUser, db: DbDep):
    await service.reset_password(db, admin, user_id, data.new_password)


# ── Реестры ──────────────────────────────────────────────────────────────────
@router.get("/payments", response_model=AdminPaymentListOut)
async def list_payments(
    db: DbDep,
    status_filter: PaymentStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return await service.list_payments(db, status=status_filter, page=page, size=size)


@router.post("/payments/{payment_id}/refund", status_code=status.HTTP_204_NO_CONTENT)
async def refund_payment(payment_id: int, admin: CurrentUser, db: DbDep):
    await service.refund_payment(db, admin, payment_id)


@router.get("/groups", response_model=AdminGroupListOut)
async def list_groups(
    db: DbDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    return await service.list_groups(db, page=page, size=size)


# ── Журнал аудита ────────────────────────────────────────────────────────────
@router.get("/audit", response_model=AdminAuditListOut)
async def audit_log(
    db: DbDep,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
):
    return await service.list_audit(db, page=page, size=size)


# ── Справочники ──────────────────────────────────────────────────────────────
@router.get("/reference", response_model=ReferenceOut)
async def reference():
    return service.reference_data()
