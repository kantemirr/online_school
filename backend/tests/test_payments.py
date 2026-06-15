"""Unit-тесты оплаты (расчёт периода и суммы)."""
from datetime import date

from app.db.enums import SubscriptionPlan
from app.modules.payments.service import (
    PRICE_ANNUAL,
    PRICE_MONTHLY,
    compute_period,
    plan_amount,
)

_TODAY = date(2026, 6, 20)


def test_period_course_year():
    start, end = compute_period(SubscriptionPlan.COURSE, _TODAY)
    assert start == _TODAY and (end - start).days == 365


def test_period_monthly():
    _, end = compute_period(SubscriptionPlan.MONTHLY, _TODAY)
    assert (end - _TODAY).days == 30


def test_amount_period_plans_fixed():
    assert plan_amount(SubscriptionPlan.MONTHLY, None) == PRICE_MONTHLY
    assert plan_amount(SubscriptionPlan.ANNUAL, None) == PRICE_ANNUAL


def test_amount_course_uses_price():
    from decimal import Decimal
    assert plan_amount(SubscriptionPlan.COURSE, Decimal("500.00")) == Decimal("500.00")
    assert plan_amount(SubscriptionPlan.COURSE, None) == Decimal("0.00")
