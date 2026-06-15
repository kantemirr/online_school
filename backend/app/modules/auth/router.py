"""HTTP-эндпоинты аутентификации (/auth)."""
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_redis
from app.modules.auth import service
from app.modules.auth.ratelimit import enforce_rate_limit
from app.modules.auth.schemas import (
    ChildLoginIn,
    LoginIn,
    LogoutIn,
    MeOut,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    RefreshIn,
    RegisterParentIn,
    TokenPair,
    VerifyEmailIn,
)

router = APIRouter(prefix="/auth", tags=["auth"])

DbDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/register", response_model=MeOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterParentIn, db: DbDep, redis: RedisDep, request: Request):
    await enforce_rate_limit(redis, "register", _client_ip(request), limit=10, window_sec=3600)
    user = await service.register_parent(db, redis, data)
    return MeOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        display_name=data.full_name,
    )


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email(data: VerifyEmailIn, db: DbDep, redis: RedisDep):
    await service.verify_email(db, redis, data.token)


@router.post("/login", response_model=TokenPair)
async def login(data: LoginIn, db: DbDep, redis: RedisDep, request: Request):
    await enforce_rate_limit(
        redis, "login", f"{_client_ip(request)}:{data.email}", limit=5, window_sec=60
    )
    return await service.login_email(db, redis, data.email, data.password)


@router.post("/login/child", response_model=TokenPair)
async def login_child(data: ChildLoginIn, db: DbDep, redis: RedisDep, request: Request):
    await enforce_rate_limit(
        redis, "login_child", f"{_client_ip(request)}:{data.login_username}", limit=5, window_sec=60
    )
    return await service.login_child(db, redis, data.login_username, data.pin)


@router.post("/refresh", response_model=TokenPair)
async def refresh(data: RefreshIn, db: DbDep, redis: RedisDep, request: Request):
    await enforce_rate_limit(redis, "refresh", _client_ip(request), limit=10, window_sec=60)
    return await service.refresh_tokens(db, redis, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: LogoutIn, redis: RedisDep):
    await service.logout(redis, data.refresh_token)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
async def password_reset_request(
    data: PasswordResetRequestIn, db: DbDep, redis: RedisDep, request: Request
):
    await enforce_rate_limit(redis, "pwdreset", _client_ip(request), limit=3, window_sec=3600)
    await service.request_password_reset(db, redis, data.email)
    return {"status": "accepted"}


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def password_reset_confirm(data: PasswordResetConfirmIn, db: DbDep, redis: RedisDep):
    await service.confirm_password_reset(db, redis, data.token, data.new_password)
