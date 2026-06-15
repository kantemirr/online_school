"""Запросы уведомлений к БД."""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification
from app.modules.users.models import StudentProfile, User


async def list_for_user(
    db: AsyncSession, user_id: int, *, unread_only: bool = False, limit: int = 50
) -> list[Notification]:
    stmt = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)
    return list(await db.scalars(stmt))


async def unread_count(db: AsyncSession, user_id: int) -> int:
    return await db.scalar(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id, Notification.is_read.is_(False)
        )
    ) or 0


async def get_owned(db: AsyncSession, user_id: int, notification_id: int) -> Notification | None:
    n = await db.get(Notification, notification_id)
    if n is None or n.user_id != user_id:
        return None
    return n


async def parent_email_of_student(db: AsyncSession, student_id: int) -> str | None:
    """Email родителя ученика (для уведомлений по ФЗ-152) или None."""
    profile = await db.get(StudentProfile, student_id)
    if profile is None or profile.parent_id is None:
        return None
    parent_user = await db.get(User, profile.parent_id)
    return parent_user.email if parent_user else None
