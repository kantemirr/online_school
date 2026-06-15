"""HTTP-эндпоинты оплаты и абонементов (роль parent, только свои)."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.auth.deps import require_roles
from app.modules.payments import service
from app.modules.payments.schemas import (
    CheckoutIn,
    CheckoutOut,
    PayIn,
    PaymentOut,
    ReceiptOut,
    SubscriptionOut,
)
from app.modules.users.models import User

router = APIRouter(tags=["payments"])
DbDep = Annotated[AsyncSession, Depends(get_db)]
ParentDep = Annotated[User, Depends(require_roles(UserRole.PARENT))]


@router.post("/payments/checkout", response_model=CheckoutOut, status_code=status.HTTP_201_CREATED)
async def checkout(data: CheckoutIn, parent: ParentDep, db: DbDep):
    return await service.checkout(db, parent, data)


@router.post("/payments/{payment_id}/pay", response_model=PaymentOut)
async def pay(payment_id: int, data: PayIn, parent: ParentDep, db: DbDep):
    return await service.pay(db, parent, payment_id, data)


@router.get("/payments", response_model=list[PaymentOut])
async def list_payments(parent: ParentDep, db: DbDep):
    return await service.list_payments(db, parent)


@router.get("/payments/{payment_id}/receipt", response_model=ReceiptOut)
async def receipt(payment_id: int, parent: ParentDep, db: DbDep):
    return await service.get_receipt(db, parent, payment_id)


@router.get("/subscriptions", response_model=list[SubscriptionOut])
async def list_subscriptions(parent: ParentDep, db: DbDep):
    return await service.list_subscriptions(db, parent)


@router.post("/subscriptions/{subscription_id}/cancel", response_model=SubscriptionOut)
async def cancel_subscription(subscription_id: int, parent: ParentDep, db: DbDep):
    return await service.cancel_subscription(db, parent, subscription_id)
