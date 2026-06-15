"""Pydantic-схемы оплаты и абонементов."""
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.db.enums import PaymentStatus, SubscriptionPlan, SubscriptionStatus


class CheckoutIn(BaseModel):
    plan: SubscriptionPlan
    course_id: int | None = None  # обязателен только для плана COURSE


class CheckoutOut(BaseModel):
    payment_id: int
    subscription_id: int
    amount: Decimal
    status: PaymentStatus
    payment_url: str  # симуляция адреса оплаты шлюза


class PayIn(BaseModel):
    outcome: Literal["paid", "failed"] = "paid"  # симуляция исхода колбэка


class PaymentOut(BaseModel):
    id: int
    subscription_id: int
    amount: Decimal
    status: PaymentStatus
    paid_at: datetime | None
    receipt_no: str | None


class SubscriptionOut(BaseModel):
    id: int
    plan: SubscriptionPlan
    course_id: int | None
    period_start: date
    period_end: date
    status: SubscriptionStatus


class ReceiptOut(BaseModel):
    receipt_no: str
    amount: Decimal
    paid_at: datetime
    plan: SubscriptionPlan
    course_id: int | None
    period_start: date
    period_end: date
    payer: str | None
