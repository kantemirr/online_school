"""Unit-тесты аналитики (доля с guard деления на ноль)."""
from app.modules.analytics.service import safe_pct


def test_safe_pct_basic():
    assert safe_pct(1, 4) == 25.0
    assert safe_pct(3, 3) == 100.0


def test_safe_pct_zero_total():
    assert safe_pct(0, 0) == 0.0
    assert safe_pct(5, 0) == 0.0
