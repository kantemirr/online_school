"""Сквозной контрольный пример (ВКР, Табл. 19).

Один тест проходит весь happy-path: регистрация родителя → подтверждение email →
оплата абонемента → создание ребёнка → вход ребёнка → запись на курс → урок →
квиз → начисление XP и достижения → уведомление → отчёт родителю + выгрузка
печатного HTML-отчёта (выходной документ). Всё синхронно и детерминированно.
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


async def test_control_example(client, redis):
    # 1. Родитель: регистрация → подтверждение email → вход
    email = f"ctrl_{uuid4().hex[:10]}@example.com"
    reg = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "Контрольный Родитель", "consent_pdn": True,
    })
    assert reg.status_code == 201
    token = await _verify_token_for(redis, reg.json()["id"])
    assert token is not None
    assert (await client.post("/auth/verify-email", json={"token": token})).status_code == 204
    pacc = (await client.post("/auth/login", json={"email": email, "password": "parentpass1"})).json()["access_token"]
    pauth = {"Authorization": f"Bearer {pacc}"}

    # 2. Родитель заводит профиль ребёнка
    username = f"cx_{uuid4().hex[:8]}"
    child = await client.post("/children", headers=pauth, json={
        "nickname": "Контролька", "birth_date": "2014-03-03", "login_username": username, "pin": "1234",
    })
    assert child.status_code == 201
    child_id = child.json()["user_id"]

    # 3. Оплата абонемента (имитация шлюза): checkout → pay → квитанция
    co = await client.post("/payments/checkout", headers=pauth, json={"plan": "monthly"})
    assert co.status_code == 201
    payment_id = co.json()["payment_id"]
    pay = await client.post(f"/payments/{payment_id}/pay", headers=pauth, json={"outcome": "paid"})
    assert pay.status_code == 200 and pay.json()["status"] == "paid" and pay.json()["receipt_no"]
    assert any(s["status"] == "active" for s in (await client.get("/subscriptions", headers=pauth)).json())
    receipt = (await client.get(f"/payments/{payment_id}/receipt", headers=pauth)).json()
    assert receipt["receipt_no"] == pay.json()["receipt_no"]

    # 4. Ребёнок входит по логину + PIN
    cacc = (await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})).json()["access_token"]
    cauth = {"Authorization": f"Bearer {cacc}"}

    # 5. Запись на демо-курс
    course_id = (await client.get("/catalog/courses", params={"q": "Python с нуля"})).json()["items"][0]["id"]
    assert (await client.post(f"/learning/courses/{course_id}/enroll", headers=cauth)).status_code == 201

    # 6. Прохождение уроков по порядку до квиза + верный ответ → урок закрыт
    passage = (await client.get(f"/learning/courses/{course_id}", headers=cauth)).json()
    lessons = [lsn for m in passage["modules"] for lsn in m["lessons"]]
    quiz_aid = None
    for lesson in lessons:
        content = await client.get(f"/learning/lessons/{lesson['id']}", headers=cauth)
        if content.status_code != 200:
            break  # дальше заблокировано
        quiz = next((a for a in content.json()["assignments"] if a["type"] == "quiz"), None)
        if quiz:
            quiz_aid = quiz["id"]
            break
        await client.post(f"/learning/lessons/{lesson['id']}/complete", headers=cauth)
    assert quiz_aid is not None
    assignment = (await client.get(f"/assignments/{quiz_aid}", headers=cauth)).json()
    # У всех вопросов демо-квиза верный вариант — индекс 0; отвечаем [0] на каждый.
    answers = {str(q["id"]): [0] for q in assignment["questions"]}
    quiz_res = await client.post(
        f"/assignments/{quiz_aid}/submit/quiz", headers=cauth, json={"answers": answers}
    )
    assert quiz_res.status_code == 200 and quiz_res.json()["result_json"]["passed"] is True

    # 7. Геймификация: начислены XP и достижение «first_lesson»
    me = (await client.get("/gamification/me", headers=cauth)).json()
    assert me["xp"] > 0
    achievements = (await client.get("/gamification/achievements", headers=cauth)).json()
    assert any(a["code"] == "first_lesson" and a["earned"] for a in achievements)

    # 8. Уведомления ученику
    assert len((await client.get("/notifications", headers=cauth)).json()) > 0
    assert (await client.get("/notifications/unread-count", headers=cauth)).json()["count"] > 0

    # 9. Родитель видит прогресс ребёнка
    overview = (await client.get("/analytics/children", headers=pauth)).json()
    assert any(c["child_id"] == child_id for c in overview["children"])
    report = (await client.get(f"/analytics/children/{child_id}", headers=pauth)).json()
    assert report["nickname"] == "Контролька"

    # 10. Выходной документ — печатный HTML-отчёт об успеваемости
    dl = await client.get(f"/analytics/children/{child_id}/report/download", headers=pauth)
    assert dl.status_code == 200
    assert "Контролька" in dl.text
