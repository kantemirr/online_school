"""Фикстуры интеграционных тестов.

Тесты ходят в реальный API (ASGITransport) поверх Postgres/Redis, поэтому
запускаются внутри контейнера: `docker compose exec backend pytest tests/integration`.
Вне инфраструктуры модуль теста пропускается (см. _infra_available).
"""
import socket

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.main import create_app

_settings = get_settings()


def infra_available() -> bool:
    for host, port in (
        (_settings.POSTGRES_HOST, _settings.POSTGRES_PORT),
        (_settings.REDIS_HOST, _settings.REDIS_PORT),
    ):
        try:
            socket.create_connection((host, port), timeout=1).close()
        except OSError:
            return False
    return True


@pytest_asyncio.fixture
async def client(monkeypatch):
    # Не дёргаем реальную очередь email — подменяем enqueue на no-op.
    async def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr("app.modules.auth.service.enqueue", _noop)

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as c:
        yield c


@pytest_asyncio.fixture
async def redis():
    from app.core.redis import redis_client

    return redis_client
