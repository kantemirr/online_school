"""Зависимости аутентификации и контроля доступа (RBAC).

Сквозная схема: Bearer access-токен → текущий пользователь → проверка роли
и (в сервисах) владения ресурсом.
"""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.exceptions import AuthError, PermissionDeniedError
from app.core.security import ACCESS, decode_token
from app.db.enums import UserRole
from app.modules.users.models import User

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    if credentials is None:
        raise AuthError("Требуется авторизация", code="not_authenticated")
    claims = decode_token(credentials.credentials, ACCESS)
    user = await db.get(User, int(claims["sub"]))
    if user is None or not user.is_active:
        raise AuthError("Пользователь не найден или неактивен", code="user_inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """Зависимость-фабрика: пропускает только указанные роли."""

    async def _checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise PermissionDeniedError("Недостаточно прав для этого действия")
        return user

    return _checker
