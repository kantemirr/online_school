"""Прикладная логика аутентификации.

Сервис не зависит от FastAPI: принимает сессию БД и клиент Redis, возвращает
доменные объекты/пары токенов, бросает доменные исключения.
"""
from datetime import datetime, timezone

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.email import password_reset_email, verification_email
from app.core.exceptions import AuthError, ConflictError
from app.core.queue import enqueue
from app.core.security import (
    REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_pin,
)
from app.modules.auth import tokens
from app.modules.auth.schemas import RegisterParentIn, TokenPair
from app.modules.users.models import ParentProfile, StudentProfile, User
from app.db.enums import UserRole

_settings = get_settings()


async def _issue_pair(redis: aioredis.Redis, user: User) -> TokenPair:
    access, _ = create_access_token(user.id, user.role.value)
    refresh, jti = create_refresh_token(user.id)
    await tokens.store_refresh(redis, user.id, jti)
    return TokenPair(access_token=access, refresh_token=refresh)


# ── Регистрация / верификация ───────────────────────────────────────────────
async def register_parent(db: AsyncSession, redis: aioredis.Redis, data: RegisterParentIn) -> User:
    exists = await db.scalar(select(User).where(User.email == data.email))
    if exists is not None:
        raise ConflictError("Пользователь с таким email уже зарегистрирован", code="email_taken")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.PARENT,
        is_active=False,
        is_email_verified=False,
    )
    user.parent_profile = ParentProfile(
        full_name=data.full_name,
        phone=data.phone,
        consent_pdn=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = await tokens.create_one_time(redis, "verify", user.id)
    link = f"{_settings.FRONTEND_BASE_URL}/verify-email?token={token}"
    subject, html = verification_email(link)
    await enqueue("send_email", to=data.email, subject=subject, html=html)
    return user


async def verify_email(db: AsyncSession, redis: aioredis.Redis, token: str) -> None:
    user_id = await tokens.consume_one_time(redis, "verify", token)
    if user_id is None:
        raise AuthError("Недействительная или просроченная ссылка", code="verify_invalid")
    user = await db.get(User, user_id)
    if user is None:
        raise AuthError("Пользователь не найден", code="user_not_found")
    user.is_active = True
    user.is_email_verified = True
    await db.commit()


# ── Вход ────────────────────────────────────────────────────────────────────
async def login_email(db: AsyncSession, redis: aioredis.Redis, email: str, password: str) -> TokenPair:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(password, user.password_hash):
        raise AuthError("Неверный email или пароль", code="bad_credentials")
    if not user.is_active:
        raise AuthError("Аккаунт не активирован — подтвердите email", code="inactive")
    return await _issue_pair(redis, user)


async def login_child(
    db: AsyncSession, redis: aioredis.Redis, login_username: str, pin: str
) -> TokenPair:
    profile = await db.scalar(
        select(StudentProfile).where(StudentProfile.login_username == login_username)
    )
    if profile is None or profile.pin_hash is None or not verify_pin(pin, profile.pin_hash):
        raise AuthError("Неверный логин или PIN", code="bad_credentials")
    user = await db.get(User, profile.user_id)
    if user is None or not user.is_active:
        raise AuthError("Аккаунт недоступен", code="inactive")
    return await _issue_pair(redis, user)


# ── Ротация / выход ──────────────────────────────────────────────────────────
async def refresh_tokens(db: AsyncSession, redis: aioredis.Redis, refresh_token: str) -> TokenPair:
    claims = decode_token(refresh_token, REFRESH)
    user_id = int(claims["sub"])
    jti = claims["jti"]
    if not await tokens.is_refresh_active(redis, user_id, jti):
        raise AuthError("Refresh-токен отозван или недействителен", code="refresh_revoked")
    # Ротация: старый jti удаляем, выдаём новую пару
    await tokens.revoke_refresh(redis, user_id, jti)
    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthError("Аккаунт недоступен", code="inactive")
    return await _issue_pair(redis, user)


async def logout(redis: aioredis.Redis, refresh_token: str) -> None:
    try:
        claims = decode_token(refresh_token, REFRESH)
    except AuthError:
        return  # истёкший/битый токен — выходить уже нечем
    await tokens.revoke_refresh(redis, int(claims["sub"]), claims["jti"])


# ── Сброс пароля ─────────────────────────────────────────────────────────────
async def request_password_reset(db: AsyncSession, redis: aioredis.Redis, email: str) -> None:
    # Не раскрываем существование аккаунта: всегда «успех».
    user = await db.scalar(select(User).where(User.email == email))
    if user is not None and user.email:
        token = await tokens.create_one_time(redis, "pwdreset", user.id)
        link = f"{_settings.FRONTEND_BASE_URL}/reset-password?token={token}"
        subject, html = password_reset_email(link)
        await enqueue("send_email", to=user.email, subject=subject, html=html)


async def confirm_password_reset(
    db: AsyncSession, redis: aioredis.Redis, token: str, new_password: str
) -> None:
    user_id = await tokens.consume_one_time(redis, "pwdreset", token)
    if user_id is None:
        raise AuthError("Недействительная или просроченная ссылка", code="reset_invalid")
    user = await db.get(User, user_id)
    if user is None:
        raise AuthError("Пользователь не найден", code="user_not_found")
    user.password_hash = hash_password(new_password)
    await db.commit()
    # Отзываем все активные refresh — после сброса нужен повторный вход
    await tokens.revoke_all_refresh(redis, user_id)
