"""Модели абонементов и платежей.

Платёжный шлюз имитируется: платёж создаётся, затем симулируется колбэк
«оплачено», после чего активируется доступ. Реальный шлюз — точка интеграции.
"""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum as SaEnum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin
from app.db.enums import PaymentStatus, SubscriptionPlan, SubscriptionStatus


class Subscription(IdMixin, Base):
    __tablename__ = "subscriptions"

    parent_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("parent_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Для тарифа COURSE — конкретный курс; для подписок period — null
    course_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("courses.id", ondelete="SET NULL")
    )
    plan: Mapped[SubscriptionPlan] = mapped_column(
        SaEnum(SubscriptionPlan, native_enum=False, length=16), nullable=False
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[SubscriptionStatus] = mapped_column(
        SaEnum(SubscriptionStatus, native_enum=False, length=16),
        default=SubscriptionStatus.PENDING,
        nullable=False,
        index=True,
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )


class Payment(IdMixin, Base):
    __tablename__ = "payments"

    subscription_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SaEnum(PaymentStatus, native_enum=False, length=16),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    receipt_no: Mapped[str | None] = mapped_column(String(64), unique=True)

    subscription: Mapped["Subscription"] = relationship(back_populates="payments")
