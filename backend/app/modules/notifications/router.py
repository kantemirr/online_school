"""HTTP-эндпоинты уведомлений (любой авторизованный, только свои)."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.modules.auth.deps import CurrentUser
from app.modules.notifications import service
from app.modules.notifications.schemas import NotificationOut, UnreadCountOut

router = APIRouter(prefix="/notifications", tags=["notifications"])
DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[NotificationOut])
async def list_notifications(
    user: CurrentUser, db: DbDep,
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
):
    return await service.list_mine(db, user.id, unread_only=unread_only, limit=limit)


@router.get("/unread-count", response_model=UnreadCountOut)
async def unread_count(user: CurrentUser, db: DbDep):
    return UnreadCountOut(count=await service.unread_count(db, user.id))


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(notification_id: int, user: CurrentUser, db: DbDep):
    await service.mark_read(db, user.id, notification_id)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(user: CurrentUser, db: DbDep):
    await service.mark_all_read(db, user.id)
