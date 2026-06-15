"""Интеграционный тест админ-панели: пользователи, блокировка, реестры, RBAC."""
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


async def _admin_auth(client) -> dict:
    r = await client.post("/auth/login", json={"email": "admin@codekids.ru", "password": "admin12345"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _register_parent(client, redis) -> tuple[dict, str, int]:
    email = f"adm_{uuid4().hex[:10]}@example.com"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "Родитель Адм", "consent_pdn": True,
    })
    uid = r.json()["id"]
    token = await _verify_token_for(redis, uid)
    await client.post("/auth/verify-email", json={"token": token})
    acc = (await client.post("/auth/login", json={"email": email, "password": "parentpass1"})).json()["access_token"]
    return {"Authorization": f"Bearer {acc}"}, email, uid


async def test_admin_user_management(client, redis):
    admin = await _admin_auth(client)

    # Создаём преподавателя через существующий POST /admin/users
    temail = f"adt_{uuid4().hex[:8]}@codekids.ru"
    tr = await client.post("/admin/users", headers=admin, json={
        "email": temail, "password": "teacherpass1", "role": "teacher", "full_name": "Преп Адм",
    })
    teacher_id = tr.json()["id"]

    parent, pemail, parent_id = await _register_parent(client, redis)

    # Список пользователей: содержит созданных, фильтр по роли и поиск по email
    lst = (await client.get("/admin/users", headers=admin, params={"role": "teacher", "size": 100})).json()
    assert lst["total"] >= 1
    assert all(u["role"] == "teacher" for u in lst["items"])

    found = (await client.get("/admin/users", headers=admin, params={"q": pemail})).json()
    assert any(u["id"] == parent_id and u["display_name"] == "Родитель Адм" for u in found["items"])

    # Деталь пользователя
    detail = (await client.get(f"/admin/users/{teacher_id}", headers=admin)).json()
    assert detail["email"] == temail and detail["is_active"] is True

    # Блокировка родителя → вход больше невозможен
    r = await client.patch(f"/admin/users/{parent_id}", headers=admin, json={"is_active": False})
    assert r.status_code == 200 and r.json()["is_active"] is False
    blocked = await client.post("/auth/login", json={"email": pemail, "password": "parentpass1"})
    assert blocked.status_code in (401, 403)

    # Разблокировка → вход снова работает
    await client.patch(f"/admin/users/{parent_id}", headers=admin, json={"is_active": True})
    ok = await client.post("/auth/login", json={"email": pemail, "password": "parentpass1"})
    assert ok.status_code == 200

    # Фильтр по неактивным находит только заблокированных (родитель уже активен снова)
    inactive = (await client.get("/admin/users", headers=admin, params={"is_active": False, "size": 100})).json()
    assert all(u["is_active"] is False for u in inactive["items"])


async def test_admin_role_guards_and_reset(client, redis):
    admin = await _admin_auth(client)
    me = (await client.get("/users/me", headers=admin)).json()

    # Нельзя заблокировать самого себя
    self_block = await client.patch(f"/admin/users/{me['id']}", headers=admin, json={"is_active": False})
    assert self_block.status_code == 409
    assert self_block.json()["error"]["code"] == "cannot_modify_self"

    # Смена роли parent → admin запрещена
    _parent, _pemail, parent_id = await _register_parent(client, redis)
    bad = await client.patch(f"/admin/users/{parent_id}", headers=admin, json={"role": "admin"})
    assert bad.status_code == 409 and bad.json()["error"]["code"] == "role_change_unsupported"

    # teacher → admin разрешена
    temail = f"adp_{uuid4().hex[:8]}@codekids.ru"
    tid = (await client.post("/admin/users", headers=admin, json={
        "email": temail, "password": "teacherpass1", "role": "teacher", "full_name": "Промо",
    })).json()["id"]
    promo = await client.patch(f"/admin/users/{tid}", headers=admin, json={"role": "admin"})
    assert promo.status_code == 200 and promo.json()["role"] == "admin"

    # Сброс пароля админом → вход новым паролем работает
    rp = await client.post(f"/admin/users/{tid}/reset-password", headers=admin, json={"new_password": "brandnew99"})
    assert rp.status_code == 204
    relog = await client.post("/auth/login", json={"email": temail, "password": "brandnew99"})
    assert relog.status_code == 200


async def test_admin_registries_and_reference(client, redis):
    admin = await _admin_auth(client)

    # Платёж: родитель оформляет MONTHLY и «оплачивает» → виден в реестре
    parent, pemail, _ = await _register_parent(client, redis)
    co = (await client.post("/payments/checkout", headers=parent, json={"plan": "monthly"})).json()
    await client.post(f"/payments/{co['payment_id']}/pay", headers=parent, json={"outcome": "paid"})

    pays = (await client.get("/admin/payments", headers=admin, params={"status": "paid", "size": 100})).json()
    assert pays["total"] >= 1
    row = next(p for p in pays["items"] if p["id"] == co["payment_id"])
    assert row["payer_email"] == pemail and row["status"] == "paid" and row["receipt_no"]

    # Группа: преподаватель создаёт группу на демо-курсе → видна в реестре
    temail = f"adg_{uuid4().hex[:8]}@codekids.ru"
    await client.post("/admin/users", headers=admin, json={
        "email": temail, "password": "teacherpass1", "role": "teacher", "full_name": "Групповод",
    })
    tauth = {"Authorization": f"Bearer {(await client.post('/auth/login', json={'email': temail, 'password': 'teacherpass1'})).json()['access_token']}"}
    course_id = (await client.get("/catalog/courses", params={"q": "Python с нуля"})).json()["items"][0]["id"]
    gid = (await client.post("/scheduling/groups", headers=tauth, json={"course_id": course_id, "name": "Реестр-группа"})).json()["id"]

    groups = (await client.get("/admin/groups", headers=admin, params={"size": 100})).json()
    grow = next(g for g in groups["items"] if g["id"] == gid)
    assert grow["teacher_name"] == "Групповод" and grow["course_title"] and grow["members"] == 0

    # Справочники
    ref = (await client.get("/admin/reference", headers=admin)).json()
    roles = {i["value"] for i in ref["sections"]["roles"]}
    assert {"student", "parent", "teacher", "admin"} <= roles
    assert "payment_statuses" in ref["sections"]


async def test_admin_rbac(client, redis):
    # Родитель не имеет доступа к админ-поверхности
    parent, _, _ = await _register_parent(client, redis)
    assert (await client.get("/admin/users", headers=parent)).status_code == 403
    assert (await client.get("/admin/payments", headers=parent)).status_code == 403
    assert (await client.get("/admin/reference", headers=parent)).status_code == 403
