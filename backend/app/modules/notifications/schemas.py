"""Pydantic-схемы уведомлений."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.db.enums import NotificationType


class NotificationOut(BaseModel):
    id: int
    type: NotificationType
    payload: Any
    is_read: bool
    created_at: datetime


class UnreadCountOut(BaseModel):
    count: int
