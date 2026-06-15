"""Pydantic-схемы админ-панели: пользователи, реестры, справочники."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.db.enums import PaymentStatus, SubscriptionPlan, UserRole


# ── Управление пользователями ────────────────────────────────────────────────
class AdminUserOut(BaseModel):
    id: int
    email: str | None
    role: UserRole
    is_active: bool
    is_email_verified: bool
    display_name: str | None = None
    created_at: datetime


class AdminUserListOut(BaseModel):
    items: list[AdminUserOut]
    total: int
    page: int
    size: int


class UpdateUserIn(BaseModel):
    """Частичное обновление: блокировка/разблокировка и/или смена роли."""

    is_active: bool | None = None
    role: UserRole | None = None


class ResetPasswordIn(BaseModel):
    new_password: str = Field(min_length=8, max_length=128)


# ── Реестр платежей ──────────────────────────────────────────────────────────
class AdminPaymentOut(BaseModel):
    id: int
    payer_email: str | None
    plan: SubscriptionPlan
    amount: Decimal
    status: PaymentStatus
    receipt_no: str | None
    paid_at: datetime | None


class AdminPaymentListOut(BaseModel):
    items: list[AdminPaymentOut]
    total: int
    page: int
    size: int


# ── Реестр групп ─────────────────────────────────────────────────────────────
class AdminGroupOut(BaseModel):
    id: int
    name: str
    teacher_name: str | None
    course_title: str | None
    members: int
    sessions: int


class AdminGroupListOut(BaseModel):
    items: list[AdminGroupOut]
    total: int
    page: int
    size: int


# ── Справочники (значения enum с подписями для выпадающих списков) ────────────
class ReferenceItem(BaseModel):
    value: str
    label: str


class ReferenceOut(BaseModel):
    sections: dict[str, list[ReferenceItem]]
