"""Логика оплаты и абонементов с имитацией платёжного шлюза."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.db.enums import (
    PaymentStatus,
    SubscriptionPlan,
    SubscriptionStatus,
)
from app.modules.catalog.models import Course
from app.modules.payments import repository as repo
from app.modules.payments.models import Payment, Subscription
from app.modules.payments.schemas import (
    CheckoutIn,
    CheckoutOut,
    PayIn,
    PaymentOut,
    ReceiptOut,
    SubscriptionOut,
)
from app.modules.users.models import ParentProfile, User

settings = get_settings()

PRICE_MONTHLY = Decimal("990.00")
PRICE_ANNUAL = Decimal("9900.00")
PERIOD_DAYS = {
    SubscriptionPlan.COURSE: 365,
    SubscriptionPlan.MONTHLY: 30,
    SubscriptionPlan.ANNUAL: 365,
}


# ── Чистые помощники (юнит-тесты) ────────────────────────────────────────────
def compute_period(plan: SubscriptionPlan, today: date) -> tuple[date, date]:
    return today, today + timedelta(days=PERIOD_DAYS[plan])


def plan_amount(plan: SubscriptionPlan, course_price: Decimal | None) -> Decimal:
    if plan == SubscriptionPlan.MONTHLY:
        return PRICE_MONTHLY
    if plan == SubscriptionPlan.ANNUAL:
        return PRICE_ANNUAL
    return course_price or Decimal("0.00")  # COURSE


def _payment_out(p: Payment) -> PaymentOut:
    return PaymentOut(
        id=p.id, subscription_id=p.subscription_id, amount=p.amount,
        status=p.status, paid_at=p.paid_at, receipt_no=p.receipt_no,
    )


def _subscription_out(s: Subscription) -> SubscriptionOut:
    return SubscriptionOut(
        id=s.id, plan=s.plan, course_id=s.course_id,
        period_start=s.period_start, period_end=s.period_end, status=s.status,
    )


async def _owned_payment(db: AsyncSession, parent: User, payment_id: int) -> tuple[Payment, Subscription]:
    payment = await repo.get_payment(db, payment_id)
    if payment is None:
        raise NotFoundError("Платёж не найден", code="payment_not_found")
    subscription = await repo.get_subscription(db, payment.subscription_id)
    if subscription is None or subscription.parent_id != parent.id:
        raise NotFoundError("Платёж не найден", code="payment_not_found")
    return payment, subscription


async def _owned_subscription(db: AsyncSession, parent: User, subscription_id: int) -> Subscription:
    subscription = await repo.get_subscription(db, subscription_id)
    if subscription is None or subscription.parent_id != parent.id:
        raise NotFoundError("Абонемент не найден", code="subscription_not_found")
    return subscription


# ── Оформление и оплата ──────────────────────────────────────────────────────
async def checkout(db: AsyncSession, parent: User, data: CheckoutIn) -> CheckoutOut:
    course_price: Decimal | None = None
    course_id: int | None = None

    if data.plan == SubscriptionPlan.COURSE:
        if data.course_id is None:
            raise ConflictError("Для плана COURSE нужен course_id", code="course_required")
        course = await db.get(Course, data.course_id)
        if course is None:
            raise NotFoundError("Курс не найден", code="course_not_found")
        course_price = course.price
        course_id = course.id

    today = date.today()
    period_start, period_end = compute_period(data.plan, today)
    amount = plan_amount(data.plan, course_price)

    subscription = Subscription(
        parent_id=parent.id, course_id=course_id, plan=data.plan,
        period_start=period_start, period_end=period_end, status=SubscriptionStatus.PENDING,
    )
    db.add(subscription)
    await db.flush()
    payment = Payment(subscription_id=subscription.id, amount=amount, status=PaymentStatus.PENDING)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return CheckoutOut(
        payment_id=payment.id, subscription_id=subscription.id, amount=amount,
        status=payment.status, payment_url=f"{settings.FRONTEND_BASE_URL}/pay/{payment.id}",
    )


async def pay(db: AsyncSession, parent: User, payment_id: int, data: PayIn) -> PaymentOut:
    """Симуляция колбэка платёжного шлюза."""
    payment, subscription = await _owned_payment(db, parent, payment_id)
    if payment.status == PaymentStatus.PAID:
        raise ConflictError("Платёж уже оплачен", code="already_paid")

    if data.outcome == "paid":
        payment.status = PaymentStatus.PAID
        payment.paid_at = datetime.now(timezone.utc)
        payment.receipt_no = f"RC-{payment.id:08d}"
        subscription.status = SubscriptionStatus.ACTIVE
        await db.commit()
        await db.refresh(payment)
        from app.modules.notifications import service as notifications
        await notifications.notify_payment(
            db, parent.id, status="paid", amount=payment.amount, receipt_no=payment.receipt_no
        )
    else:
        payment.status = PaymentStatus.FAILED
        await db.commit()
        await db.refresh(payment)
        from app.modules.notifications import service as notifications
        await notifications.notify_payment(
            db, parent.id, status="failed", amount=payment.amount, receipt_no=None
        )
    return _payment_out(payment)


# ── Чтение ───────────────────────────────────────────────────────────────────
async def list_payments(db: AsyncSession, parent: User) -> list[PaymentOut]:
    return [_payment_out(p) for p in await repo.parent_payments(db, parent.id)]


async def list_subscriptions(db: AsyncSession, parent: User) -> list[SubscriptionOut]:
    return [_subscription_out(s) for s in await repo.parent_subscriptions(db, parent.id)]


async def get_receipt(db: AsyncSession, parent: User, payment_id: int) -> ReceiptOut:
    payment, subscription = await _owned_payment(db, parent, payment_id)
    if payment.status != PaymentStatus.PAID:
        raise ConflictError("Квитанция доступна только для оплаченного платежа", code="not_paid")
    profile = await db.get(ParentProfile, parent.id)
    return ReceiptOut(
        receipt_no=payment.receipt_no, amount=payment.amount, paid_at=payment.paid_at,
        plan=subscription.plan, course_id=subscription.course_id,
        period_start=subscription.period_start, period_end=subscription.period_end,
        payer=profile.full_name if profile else None,
    )


async def cancel_subscription(db: AsyncSession, parent: User, subscription_id: int) -> SubscriptionOut:
    subscription = await _owned_subscription(db, parent, subscription_id)
    if subscription.status == SubscriptionStatus.CANCELLED:
        raise ConflictError("Абонемент уже отменён", code="already_cancelled")
    subscription.status = SubscriptionStatus.CANCELLED
    await db.commit()
    await db.refresh(subscription)
    return _subscription_out(subscription)


# ── Возврат платежа (действие администратора) ────────────────────────────────
async def refund(db: AsyncSession, payment_id: int) -> PaymentOut:
    """Возврат оплаченного платежа: статус REFUNDED + снятие доступа (абонемент отменяется)."""
    payment = await repo.get_payment(db, payment_id)
    if payment is None:
        raise NotFoundError("Платёж не найден", code="payment_not_found")
    if payment.status != PaymentStatus.PAID:
        raise ConflictError("Возврат доступен только для оплаченного платежа", code="not_paid")

    payment.status = PaymentStatus.REFUNDED
    subscription = await repo.get_subscription(db, payment.subscription_id)
    if subscription is not None:
        subscription.status = SubscriptionStatus.CANCELLED
    await db.commit()
    await db.refresh(payment)

    if subscription is not None:
        from app.modules.notifications import service as notifications
        await notifications.notify_payment(
            db, subscription.parent_id, status="refunded",
            amount=payment.amount, receipt_no=payment.receipt_no,
        )
    return _payment_out(payment)


# ── Контроль доступа (стык с learning) ───────────────────────────────────────
async def has_access(db: AsyncSession, student_id: int, course: Course) -> bool:
    if course.price == 0:
        return True  # бесплатный курс открыт всем
    parent_id = await repo.parent_id_of_student(db, student_id)
    if parent_id is None:
        return False
    today = date.today()
    for subscription in await repo.active_subscriptions(db, parent_id, today):
        if subscription.plan in (SubscriptionPlan.MONTHLY, SubscriptionPlan.ANNUAL):
            return True  # подписка на период покрывает все курсы
        if subscription.plan == SubscriptionPlan.COURSE and subscription.course_id == course.id:
            return True
    return False


# ── Фоновое истечение ────────────────────────────────────────────────────────
async def expire_subscriptions(db: AsyncSession) -> int:
    today = date.today()
    expired = await repo.expired_active(db, today)
    for subscription in expired:
        subscription.status = SubscriptionStatus.EXPIRED
    if expired:
        await db.commit()
    return len(expired)
