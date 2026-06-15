"""Создание первого администратора из переменных окружения.

Запуск: `python -m app.modules.auth.bootstrap`
Идемпотентно: если админ с таким email уже есть — ничего не делает.
"""
import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.enums import UserRole
from app.db.session import SessionLocal
from app.modules.users.models import User

_settings = get_settings()


async def bootstrap_admin() -> bool:
    async with SessionLocal() as session:
        existing = await session.scalar(
            select(User).where(User.email == _settings.BOOTSTRAP_ADMIN_EMAIL)
        )
        if existing is not None:
            return False
        admin = User(
            email=_settings.BOOTSTRAP_ADMIN_EMAIL,
            password_hash=hash_password(_settings.BOOTSTRAP_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        session.add(admin)
        await session.commit()
        return True


async def main() -> None:
    created = await bootstrap_admin()
    print(
        f"bootstrap admin: {'создан' if created else 'уже существует'} "
        f"({_settings.BOOTSTRAP_ADMIN_EMAIL})"
    )


if __name__ == "__main__":
    asyncio.run(main())
