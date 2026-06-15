"""Unit-тесты расписания (валидация времени занятия)."""
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.modules.scheduling.schemas import SessionCreate

_NOW = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)


def test_valid_session_times():
    s = SessionCreate(starts_at=_NOW, ends_at=_NOW + timedelta(hours=1))
    assert s.ends_at > s.starts_at


def test_end_equal_start_rejected():
    with pytest.raises(ValidationError):
        SessionCreate(starts_at=_NOW, ends_at=_NOW)


def test_end_before_start_rejected():
    with pytest.raises(ValidationError):
        SessionCreate(starts_at=_NOW, ends_at=_NOW - timedelta(hours=1))
