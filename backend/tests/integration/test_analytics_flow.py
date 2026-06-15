"""Интеграционный тест аналитики: дашборды по ролям + RBAC."""
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


async def _parent_with_child(client, redis):
    email = f"an_{uuid4().hex[:10]}@example.com"
    username = f"an_{uuid4().hex[:8]}"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "Родитель А", "consent_pdn": True,
    })
    token = await _verify_token_for(redis, r.json()["id"])
    await client.post("/auth/verify-email", json={"token": token})
    pacc = (await client.post("/auth/login", json={"email": email, "password": "parentpass1"})).json()["access_token"]
    pauth = {"Authorization": f"Bearer {pacc}"}
    await client.post("/children", headers=pauth, json={
        "nickname": "Аналитик", "birth_date": "2014-01-01", "login_username": username, "pin": "1234",
    })
    cacc = (await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})).json()["access_token"]
    cauth = {"Authorization": f"Bearer {cacc}"}
    cid = (await client.get("/users/me", headers=cauth)).json()["id"]
    return pauth, cauth, cid


async def _teacher(client) -> str:
    a = await client.post("/auth/login", json={"email": "admin@codekids.ru", "password": "admin12345"})
    admin_auth = {"Authorization": f"Bearer {a.json()['access_token']}"}
    email = f"at_{uuid4().hex[:8]}@codekids.ru"
    await client.post("/admin/users", headers=admin_auth, json={
        "email": email, "password": "teacherpass1", "role": "teacher", "full_name": "T",
    })
    return (await client.post("/auth/login", json={"email": email, "password": "teacherpass1"})).json()["access_token"]


async def test_analytics_dashboards(client, redis):
    pauth, cauth, child_id = await _parent_with_child(client, redis)

    course_id = (await client.get("/catalog/courses", params={"q": "Python с нуля"})).json()["items"][0]["id"]
    await client.post(f"/learning/courses/{course_id}/enroll", headers=cauth)
    passage = (await client.get(f"/learning/courses/{course_id}", headers=cauth)).json()
    first_lesson = passage["modules"][0]["lessons"][0]["id"]
    await client.post(f"/learning/lessons/{first_lesson}/complete", headers=cauth)

    # Ученик: дашборд
    me = (await client.get("/analytics/me", headers=cauth)).json()
    assert me["xp"] > 0
    assert any(c["course_id"] == course_id for c in me["courses"])

    # Родитель: список детей + расходы, детальный отчёт ребёнка
    parent = (await client.get("/analytics/children", headers=pauth)).json()
    assert any(ch["child_id"] == child_id for ch in parent["children"])
    assert "total_spent" in parent["expenses"]
    report = (await client.get(f"/analytics/children/{child_id}", headers=pauth)).json()
    assert report["nickname"] == "Аналитик"
    assert any(a["code"] == "first_lesson" for a in report["achievements"])
    assert "rate" in report["attendance"]

    # Преподаватель: аналитика группы (с посещаемостью)
    tauth = {"Authorization": f"Bearer {await _teacher(client)}"}
    gid = (await client.post("/scheduling/groups", headers=tauth, json={"course_id": course_id, "name": "AG"})).json()["id"]
    await client.post(f"/scheduling/groups/{gid}/members", headers=tauth, json={"student_id": child_id})
    sid = (await client.post(f"/scheduling/groups/{gid}/sessions", headers=tauth, json={
        "starts_at": "2026-07-05T10:00:00Z", "ends_at": "2026-07-05T11:00:00Z",
    })).json()["id"]
    await client.post(f"/scheduling/sessions/{sid}/attendance", headers=tauth, json={
        "records": [{"student_id": child_id, "status": "present"}],
    })
    ga = (await client.get(f"/analytics/groups/{gid}", headers=tauth)).json()
    assert ga["group_id"] == gid
    row = next(r for r in ga["students"] if r["student_id"] == child_id)
    assert row["attendance_rate"] == 100.0

    # Админ: сводка
    aauth = {"Authorization": f"Bearer {(await client.post('/auth/login', json={'email': 'admin@codekids.ru', 'password': 'admin12345'})).json()['access_token']}"}
    overview = (await client.get("/analytics/admin/overview", headers=aauth)).json()
    assert overview["users"]["total"] > 0
    assert overview["enrollments"] > 0

    # RBAC
    other_pauth, _, _ = await _parent_with_child(client, redis)
    r = await client.get(f"/analytics/children/{child_id}", headers=other_pauth)
    assert r.status_code == 404  # чужой ребёнок
    r = await client.get("/analytics/admin/overview", headers=cauth)
    assert r.status_code == 403  # ученик не админ
