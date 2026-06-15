"""Запись в журнал аудита ключевых действий."""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.models import AuditLog
from app.modules.users.models import User


async def record_audit(
    db: AsyncSession,
    actor: User | None,
    action: str,
    *,
    target: str | None = None,
    meta: Any = None,
) -> None:
    """Добавляет запись аудита и коммитит (вызывать после основного действия)."""
    db.add(
        AuditLog(
            actor_id=getattr(actor, "id", None),
            actor_email=getattr(actor, "email", None),
            action=action,
            target=target,
            meta_json=meta,
        )
    )
    await db.commit()
