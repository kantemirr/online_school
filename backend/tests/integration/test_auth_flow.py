"""Сквозной интеграционный тест аутентификации и RBAC.

Покрывает: регистрация → верификация → вход → /me → создание ребёнка →
вход ребёнка по PIN → ротация refresh (старый отозван) → RBAC 403.
"""
from uuid import uuid4

import pytest

from tests.integration.conftest import infra_available

if not infra_available():
    pytest.skip("нужны Postgres/Redis (запуск в контейнере)", allow_module_level=True)

# Все тесты пакета — на одном session-loop (общий пул Redis).
pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _verify_token_for(redis, user_id: int) -> str | None:
    async for key in redis.scan_iter(match="auth:verify:*"):
        if await redis.get(key) == str(user_id):
            return key.split(":")[-1]
    return None


async def test_full_auth_flow(client, redis):
    email = f"parent_{uuid4().hex[:10]}@example.com"
    username = f"kid_{uuid4().hex[:8]}"

    # 0. Неверный логин/PIN ребёнка отклоняется
    r = await client.post("/auth/login/child", json={"login_username": "nobody", "pin": "0000"})
    assert r.status_code == 401

    # 1. Регистрация родителя
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1",
        "full_name": "Тест Родитель", "consent_pdn": True,
    })
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]
    assert r.json()["is_active"] is False

    # 2. Вход до верификации запрещён
    r = await client.post("/auth/login", json={"email": email, "password": "parentpass1"})
    assert r.status_code == 401

    # 3. Верификация по токену из Redis
    token = await _verify_token_for(redis, user_id)
    assert token is not None
    r = await client.post("/auth/verify-email", json={"token": token})
    assert r.status_code == 204

    # 4. Вход после верификации
    r = await client.post("/auth/login", json={"email": email, "password": "parentpass1"})
    assert r.status_code == 200
    access = r.json()["access_token"]
    refresh = r.json()["refresh_token"]
    auth = {"Authorization": f"Bearer {access}"}

    # 5. Профиль
    r = await client.get("/users/me", headers=auth)
    assert r.status_code == 200 and r.json()["role"] == "parent"

    # 6. Создание ребёнка + возрастная группа
    r = await client.post("/children", headers=auth, json={
        "nickname": "Котёнок", "birth_date": "2015-05-01",
        "login_username": username, "pin": "1234",
    })
    assert r.status_code == 201, r.text
    assert r.json()["age_group"] in {"junior", "middle", "senior"}

    # 7. Вход ребёнка по PIN
    r = await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})
    assert r.status_code == 200

    # 8. Ротация refresh: новый выдаётся, старый отзывается
    r = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    r = await client.post("/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401  # старый refresh уже невалиден

    # 9. RBAC: родитель не может создавать персонал
    r = await client.post("/admin/users", headers=auth, json={
        "email": f"t_{uuid4().hex[:6]}@example.com", "password": "teacherpass1",
        "role": "teacher", "full_name": "T",
    })
    assert r.status_code == 403
