"""Интеграционный тест автопроверки квиза (в контейнере).

Код-задания требуют воркер+Docker, поэтому проверяются живым прогоном; здесь —
ASGI-путь квиза: решение → мгновенная оценка → закрытие урока.
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
    email = f"grade_{uuid4().hex[:10]}@example.com"
    username = f"gr_{uuid4().hex[:8]}"
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


async def test_quiz_autocheck_completes_lesson(client, redis):
    auth = {"Authorization": f"Bearer {await _make_student(client, redis)}"}

    # Демо-курс Python
    r = await client.get("/catalog/courses", params={"q": "Python"})
    course_id = r.json()["items"][0]["id"]
    await client.post(f"/learning/courses/{course_id}/enroll", headers=auth)

    # Найти урок с квизом, открыв уроки по порядку
    passage = (await client.get(f"/learning/courses/{course_id}", headers=auth)).json()
    lessons = [l for m in passage["modules"] for l in m["lessons"]]

    quiz_assignment_id = None
    for lesson in lessons:
        content = await client.get(f"/learning/lessons/{lesson['id']}", headers=auth)
        if content.status_code != 200:
            break  # дальше заблокировано
        quiz = next((a for a in content.json()["assignments"] if a["type"] == "quiz"), None)
        if quiz:
            quiz_assignment_id = quiz["id"]
            break
        # урок без квиза — завершаем, чтобы открыть следующий
        await client.post(f"/learning/lessons/{lesson['id']}/complete", headers=auth)

    assert quiz_assignment_id is not None

    # Получить вопросы и отправить верный ответ (демо: верный вариант — индекс 0)
    assignment = (await client.get(f"/assignments/{quiz_assignment_id}", headers=auth)).json()
    answers = {str(q["id"]): [0] for q in assignment["questions"]}
    r = await client.post(
        f"/assignments/{quiz_assignment_id}/submit/quiz",
        headers=auth, json={"answers": answers},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "checked"
    assert body["result_json"]["passed"] is True
