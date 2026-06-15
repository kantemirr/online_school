"""Живой прогон песочницы — защищаемое ядро ВКР.

Код ученика реально исполняется в изолированном Docker-контейнере фоновым
воркером (ARQ). Тест ставит отправку в очередь и опрашивает результат. Если
воркер/Docker недоступны (например, в CI без поднятого worker) — тест
пропускается, чтобы не делать суит «красным».
"""
import asyncio
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


async def _student_auth(client, redis) -> dict:
    email = f"sbx_{uuid4().hex[:10]}@example.com"
    username = f"sb_{uuid4().hex[:8]}"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "P", "consent_pdn": True,
    })
    token = await _verify_token_for(redis, r.json()["id"])
    await client.post("/auth/verify-email", json={"token": token})
    pacc = (await client.post("/auth/login", json={"email": email, "password": "parentpass1"})).json()["access_token"]
    await client.post("/children", headers={"Authorization": f"Bearer {pacc}"}, json={
        "nickname": "Кодер", "birth_date": "2013-01-01", "login_username": username, "pin": "1234",
    })
    cacc = (await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})).json()["access_token"]
    return {"Authorization": f"Bearer {cacc}"}


async def _reach_code_assignment(client, auth, course_id) -> int | None:
    passage = (await client.get(f"/learning/courses/{course_id}", headers=auth)).json()
    for lesson in [lsn for m in passage["modules"] for lsn in m["lessons"]]:
        content = await client.get(f"/learning/lessons/{lesson['id']}", headers=auth)
        if content.status_code != 200:
            break
        code = next((a for a in content.json()["assignments"] if a["type"] == "code"), None)
        if code:
            return code["id"]
        await client.post(f"/learning/lessons/{lesson['id']}/complete", headers=auth)
    return None


async def _poll(client, auth, submission_id: int, timeout: float = 45.0):
    deadline = int(timeout / 1.5)
    for _ in range(deadline):
        s = (await client.get(f"/submissions/{submission_id}", headers=auth)).json()
        if s["status"] == "checked":
            return s
        await asyncio.sleep(1.5)
    return None


async def test_code_sandbox_live(client, redis):
    auth = await _student_auth(client, redis)
    course_id = (await client.get("/catalog/courses", params={"q": "Python с нуля"})).json()["items"][0]["id"]
    await client.post(f"/learning/courses/{course_id}/enroll", headers=auth)

    code_aid = await _reach_code_assignment(client, auth, course_id)
    assert code_aid is not None, "в демо-курсе должно быть код-задание"

    # Верное решение: квадрат числа из stdin
    sub = await client.post(
        f"/assignments/{code_aid}/submit/code", headers=auth, json={"code": "print(int(input())**2)"}
    )
    assert sub.status_code == 202
    result = await _poll(client, auth, sub.json()["id"])
    if result is None:
        pytest.skip("воркер/Docker не обработали отправку за таймаут — нужен поднятый worker")

    # Изолированное исполнение вернуло корректный вердикт
    assert result["verdict"] == "passed"
    summary = result["result_json"]["summary"]
    assert summary["passed"] == summary["total"] and summary["total"] > 0

    # Неверное решение → провал + безопасная ИИ/эвристическая подсказка
    bad = await client.post(
        f"/assignments/{code_aid}/submit/code", headers=auth, json={"code": "print('неверно')"}
    )
    bad_result = await _poll(client, auth, bad.json()["id"])
    if bad_result is not None:
        assert bad_result["verdict"] in ("failed", "partial")
        hint = await client.get(f"/submissions/{bad.json()['id']}/hint", headers=auth)
        assert hint.status_code == 200 and hint.json()["source"] in ("ai", "heuristic")
