"""Запросы оплаты/абонементов к БД."""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import SubscriptionStatus
from app.modules.payments.models import Payment, Subscription
from app.modules.users.models import StudentProfile


async def get_subscription(db: AsyncSession, subscription_id: int) -> Subscription | None:
    return await db.get(Subscription, subscription_id)


async def get_payment(db: AsyncSession, payment_id: int) -> Payment | None:
    return await db.get(Payment, payment_id)


async def parent_payments(db: AsyncSession, parent_id: int) -> list[Payment]:
    return list(await db.scalars(
        select(Payment)
        .join(Subscription, Subscription.id == Payment.subscription_id)
        .where(Subscription.parent_id == parent_id)
        .order_by(Payment.id.desc())
    ))


async def parent_subscriptions(db: AsyncSession, parent_id: int) -> list[Subscription]:
    return list(await db.scalars(
        select(Subscription).where(Subscription.parent_id == parent_id).order_by(Subscription.id.desc())
    ))


async def active_subscriptions(db: AsyncSession, parent_id: int, today: date) -> list[Subscription]:
    return list(await db.scalars(
        select(Subscription).where(
            Subscription.parent_id == parent_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.period_end >= today,
        )
    ))


async def parent_id_of_student(db: AsyncSession, student_id: int) -> int | None:
    profile = await db.get(StudentProfile, student_id)
    return profile.parent_id if profile else None


async def expired_active(db: AsyncSession, today: date) -> list[Subscription]:
    return list(await db.scalars(
        select(Subscription).where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.period_end < today,
        )
    ))
