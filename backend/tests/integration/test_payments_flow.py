"""Интеграционный тест оплаты: гейт доступа, имитация шлюза, квитанция, отмена."""
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


async def _parent_with_child(client, redis) -> tuple[dict, dict, int]:
    """Возвращает (parent_auth, child_auth, child_id)."""
    email = f"pay_{uuid4().hex[:10]}@example.com"
    username = f"py_{uuid4().hex[:8]}"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "Плательщик", "consent_pdn": True,
    })
    token = await _verify_token_for(redis, r.json()["id"])
    await client.post("/auth/verify-email", json={"token": token})
    pacc = (await client.post("/auth/login", json={"email": email, "password": "parentpass1"})).json()["access_token"]
    pauth = {"Authorization": f"Bearer {pacc}"}
    await client.post("/children", headers=pauth, json={
        "nickname": "Дитя", "birth_date": "2014-01-01", "login_username": username, "pin": "1234",
    })
    cacc = (await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})).json()["access_token"]
    cauth = {"Authorization": f"Bearer {cacc}"}
    cid = (await client.get("/users/me", headers=cauth)).json()["id"]
    return pauth, cauth, cid


async def _make_paid_course(client) -> int:
    a = await client.post("/auth/login", json={"email": "admin@codekids.ru", "password": "admin12345"})
    admin_auth = {"Authorization": f"Bearer {a.json()['access_token']}"}
    r = await client.post("/admin/catalog/courses", headers=admin_auth, json={
        "title": f"Платный курс {uuid4().hex[:6]}", "track": "python", "level": "beginner",
        "price": "990.00",
    })
    cid = r.json()["id"]
    await client.post(f"/admin/catalog/courses/{cid}/publish", headers=admin_auth)
    return cid


async def test_payment_gates_paid_course(client, redis):
    pauth, cauth, child_id = await _parent_with_child(client, redis)
    paid_course = await _make_paid_course(client)

    # Без абонемента платный курс недоступен
    r = await client.post(f"/learning/courses/{paid_course}/enroll", headers=cauth)
    assert r.status_code == 403

    # Бесплатный демо-курс доступен без оплаты
    free_course = (await client.get("/catalog/courses", params={"q": "Python с нуля"})).json()["items"][0]["id"]
    r = await client.post(f"/learning/courses/{free_course}/enroll", headers=cauth)
    assert r.status_code == 201

    # RBAC: ученик не может оформлять оплату
    r = await client.post("/payments/checkout", headers=cauth, json={"plan": "course", "course_id": paid_course})
    assert r.status_code == 403

    # COURSE без course_id → ошибка
    r = await client.post("/payments/checkout", headers=pauth, json={"plan": "course"})
    assert r.status_code == 409

    # Оформление и «оплата» (имитация колбэка)
    co = await client.post("/payments/checkout", headers=pauth, json={"plan": "course", "course_id": paid_course})
    assert co.status_code == 201 and co.json()["status"] == "pending"
    payment_id = co.json()["payment_id"]
    sub_id = co.json()["subscription_id"]

    pr = await client.post(f"/payments/{payment_id}/pay", headers=pauth, json={"outcome": "paid"})
    assert pr.status_code == 200 and pr.json()["status"] == "paid" and pr.json()["receipt_no"]

    # Повторная оплата идемпотентна → 409
    again = await client.post(f"/payments/{payment_id}/pay", headers=pauth, json={"outcome": "paid"})
    assert again.status_code == 409

    # Теперь ребёнок может записаться на платный курс
    r = await client.post(f"/learning/courses/{paid_course}/enroll", headers=cauth)
    assert r.status_code == 201

    # История, квитанция, подписки
    history = (await client.get("/payments", headers=pauth)).json()
    assert any(p["id"] == payment_id and p["status"] == "paid" for p in history)
    receipt = (await client.get(f"/payments/{payment_id}/receipt", headers=pauth)).json()
    assert receipt["receipt_no"] == pr.json()["receipt_no"] and receipt["payer"] == "Плательщик"
    subs = (await client.get("/subscriptions", headers=pauth)).json()
    assert any(s["id"] == sub_id and s["status"] == "active" for s in subs)

    # Отмена снимает доступ: второй ребёнок того же родителя не запишется
    cancel = await client.post(f"/subscriptions/{sub_id}/cancel", headers=pauth)
    assert cancel.status_code == 200 and cancel.json()["status"] == "cancelled"
    again_cancel = await client.post(f"/subscriptions/{sub_id}/cancel", headers=pauth)
    assert again_cancel.status_code == 409

    username2 = f"py2_{uuid4().hex[:8]}"
    await client.post("/children", headers=pauth, json={
        "nickname": "Второй", "birth_date": "2015-01-01", "login_username": username2, "pin": "4321",
    })
    c2 = (await client.post("/auth/login/child", json={"login_username": username2, "pin": "4321"})).json()["access_token"]
    r = await client.post(f"/learning/courses/{paid_course}/enroll", headers={"Authorization": f"Bearer {c2}"})
    assert r.status_code == 403  # абонемент отменён → доступа нет
