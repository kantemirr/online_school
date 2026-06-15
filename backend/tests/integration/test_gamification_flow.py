"""Интеграционный тест геймификации: завершение урока → XP, достижение, лидерборд."""
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
    email = f"gam_{uuid4().hex[:10]}@example.com"
    username = f"gm_{uuid4().hex[:8]}"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "P", "consent_pdn": True,
    })
    token = await _verify_token_for(redis, r.json()["id"])
    await client.post("/auth/verify-email", json={"token": token})
    p = await client.post("/auth/login", json={"email": email, "password": "parentpass1"})
    pacc = p.json()["access_token"]
    await client.post("/children", headers={"Authorization": f"Bearer {pacc}"}, json={
        "nickname": "N", "birth_date": "2014-01-01", "login_username": username, "pin": "1234",
    })
    c = await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})
    return c.json()["access_token"]


async def test_gamification_award_on_lesson_complete(client, redis):
    auth = {"Authorization": f"Bearer {await _make_student(client, redis)}"}

    r = await client.get("/catalog/courses", params={"q": "Python"})
    course_id = r.json()["items"][0]["id"]
    await client.post(f"/learning/courses/{course_id}/enroll", headers=auth)

    # До начислений
    before = (await client.get("/gamification/me", headers=auth)).json()
    assert before["xp"] == 0
    assert before["achievements_earned"] == 0

    # Завершаем первый урок
    passage = (await client.get(f"/learning/courses/{course_id}", headers=auth)).json()
    first_lesson_id = passage["modules"][0]["lessons"][0]["id"]
    await client.post(f"/learning/lessons/{first_lesson_id}/complete", headers=auth)

    # XP начислен, streak=1, достижение first_lesson выдано
    after = (await client.get("/gamification/me", headers=auth)).json()
    assert after["xp"] > 0
    assert after["streak"] == 1
    assert after["achievements_earned"] >= 1

    achievements = (await client.get("/gamification/achievements", headers=auth)).json()
    first = next(a for a in achievements if a["code"] == "first_lesson")
    assert first["earned"] is True

    # Ученик присутствует в глобальном лидерборде
    lb = (await client.get("/gamification/leaderboard", headers=auth)).json()
    assert lb["my_rank"] is not None
    assert lb["my_score"] == after["xp"]
