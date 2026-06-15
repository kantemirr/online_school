"""Сквозной интеграционный тест каталога и прохождения (в контейнере).

Один тест-функция (один event loop) — чтобы не ловить пересечение циклов с
глобальным пулом Redis.
"""
from uuid import uuid4

import pytest

from tests.integration.conftest import infra_available

if not infra_available():
    pytest.skip("нужны Postgres/Redis (запуск в контейнере)", allow_module_level=True)

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def _verify_token_for(redis, user_id: int) -> str | None:
    async for key in redis.scan_iter(match="auth:verify:*"):
        if await redis.get(key) == str(user_id):
            return key.split(":")[-1]
    return None


async def _make_student(client, redis) -> str:
    """Регистрирует родителя, заводит ребёнка, возвращает access-токен ребёнка."""
    email = f"flow_{uuid4().hex[:10]}@example.com"
    username = f"st_{uuid4().hex[:8]}"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "P", "consent_pdn": True,
    })
    uid = r.json()["id"]
    token = await _verify_token_for(redis, uid)
    await client.post("/auth/verify-email", json={"token": token})
    p = await client.post("/auth/login", json={"email": email, "password": "parentpass1"})
    pacc = p.json()["access_token"]
    await client.post("/children", headers={"Authorization": f"Bearer {pacc}"}, json={
        "nickname": "N", "birth_date": "2014-01-01", "login_username": username, "pin": "1234",
    })
    c = await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})
    return c.json()["access_token"]


async def test_catalog_and_learning_flow(client, redis):
    # ── Каталог: список и поиск демо-курса ──
    r = await client.get("/catalog/courses", params={"q": "Python"})
    assert r.status_code == 200
    assert r.json()["total"] >= 1
    course = r.json()["items"][0]
    course_id = course["id"]

    r = await client.get(f"/catalog/courses/{course_id}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["lesson_count"] >= 1
    first_lesson_id = detail["modules"][0]["lessons"][0]["id"]

    # ── Admin: создать и опубликовать курс (инвалидация кэша) ──
    a = await client.post("/auth/login", json={"email": "admin@codekids.ru", "password": "admin12345"})
    admin_auth = {"Authorization": f"Bearer {a.json()['access_token']}"}
    r = await client.post("/admin/catalog/courses", headers=admin_auth, json={
        "title": f"Тест-курс {uuid4().hex[:6]}", "track": "web", "level": "beginner",
    })
    assert r.status_code == 201
    new_id = r.json()["id"]
    r = await client.post(f"/admin/catalog/courses/{new_id}/publish", headers=admin_auth)
    assert r.status_code == 200
    r = await client.get("/catalog/courses", params={"track": "web"})
    assert any(c["id"] == new_id for c in r.json()["items"])  # кэш сброшен

    # ── Ученик ──
    sacc = await _make_student(client, redis)
    sauth = {"Authorization": f"Bearer {sacc}"}

    # RBAC: ученик не может управлять контентом
    r = await client.post("/admin/catalog/courses", headers=sauth, json={
        "title": "x", "track": "python", "level": "beginner",
    })
    assert r.status_code == 403

    # ── Прохождение ──
    r = await client.post(f"/learning/courses/{course_id}/enroll", headers=sauth)
    assert r.status_code == 201

    r = await client.get(f"/learning/courses/{course_id}", headers=sauth)
    passage = r.json()
    lessons = [l for m in passage["modules"] for l in m["lessons"]]
    assert lessons[0]["locked"] is False
    if len(lessons) > 1:
        assert lessons[1]["locked"] is True  # второй заблокирован

    # Контент первого урока доступен
    r = await client.get(f"/learning/lessons/{first_lesson_id}", headers=sauth)
    assert r.status_code == 200

    # Завершение первого урока повышает прогресс и разблокирует следующий
    r = await client.post(f"/learning/lessons/{first_lesson_id}/complete", headers=sauth)
    assert r.status_code == 200
    after = r.json()
    assert after["progress_pct"] > 0
    after_lessons = [l for m in after["modules"] for l in m["lessons"]]
    assert after_lessons[0]["status"] == "completed"
