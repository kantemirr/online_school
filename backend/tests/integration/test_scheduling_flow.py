"""Интеграционный тест групп/расписания/посещаемости (в контейнере)."""
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


async def _make_student(client, redis) -> tuple[str, int]:
    email = f"sch_{uuid4().hex[:10]}@example.com"
    username = f"sc_{uuid4().hex[:8]}"
    r = await client.post("/auth/register", json={
        "email": email, "password": "parentpass1", "full_name": "P", "consent_pdn": True,
    })
    token = await _verify_token_for(redis, r.json()["id"])
    await client.post("/auth/verify-email", json={"token": token})
    pacc = (await client.post("/auth/login", json={"email": email, "password": "parentpass1"})).json()["access_token"]
    await client.post("/children", headers={"Authorization": f"Bearer {pacc}"}, json={
        "nickname": "N", "birth_date": "2014-01-01", "login_username": username, "pin": "1234",
    })
    sacc = (await client.post("/auth/login/child", json={"login_username": username, "pin": "1234"})).json()["access_token"]
    sauth = {"Authorization": f"Bearer {sacc}"}
    sid = (await client.get("/users/me", headers=sauth)).json()["id"]
    return sacc, sid


async def _make_teacher(client) -> str:
    a = await client.post("/auth/login", json={"email": "admin@codekids.ru", "password": "admin12345"})
    admin_auth = {"Authorization": f"Bearer {a.json()['access_token']}"}
    email = f"teach_{uuid4().hex[:8]}@codekids.ru"
    await client.post("/admin/users", headers=admin_auth, json={
        "email": email, "password": "teacherpass1", "role": "teacher", "full_name": "T",
    })
    t = await client.post("/auth/login", json={"email": email, "password": "teacherpass1"})
    return t.json()["access_token"]


async def test_scheduling_flow(client, redis):
    sacc, student_id = await _make_student(client, redis)
    sauth = {"Authorization": f"Bearer {sacc}"}
    tauth = {"Authorization": f"Bearer {await _make_teacher(client)}"}

    course_id = (await client.get("/catalog/courses", params={"q": "Python"})).json()["items"][0]["id"]

    # RBAC: ученик не может создавать группы
    r = await client.post("/scheduling/groups", headers=sauth, json={"course_id": course_id, "name": "X"})
    assert r.status_code == 403

    # Преподаватель: группа → ученик → занятие → посещаемость
    r = await client.post("/scheduling/groups", headers=tauth, json={"course_id": course_id, "name": "Группа А"})
    assert r.status_code == 201
    group_id = r.json()["id"]

    r = await client.post(f"/scheduling/groups/{group_id}/members", headers=tauth, json={"student_id": student_id})
    assert r.status_code == 204

    r = await client.post(f"/scheduling/groups/{group_id}/sessions", headers=tauth, json={
        "starts_at": "2026-06-25T10:00:00Z", "ends_at": "2026-06-25T11:00:00Z",
        "meeting_url": "https://meet.jit.si/codekids-a",
    })
    assert r.status_code == 201
    session_id = r.json()["id"]

    r = await client.post(f"/scheduling/sessions/{session_id}/attendance", headers=tauth, json={
        "records": [{"student_id": student_id, "status": "present"}],
    })
    assert r.status_code == 204

    att = (await client.get(f"/scheduling/sessions/{session_id}/attendance", headers=tauth)).json()
    assert any(a["student_id"] == student_id and a["status"] == "present" for a in att)

    # Ученик видит свои группу, расписание, посещаемость
    groups = (await client.get("/scheduling/my/groups", headers=sauth)).json()
    assert any(g["group_id"] == group_id for g in groups)
    schedule = (await client.get("/scheduling/my/schedule", headers=sauth)).json()
    assert any(s["session_id"] == session_id and s["meeting_url"] for s in schedule)
    my_att = (await client.get("/scheduling/my/attendance", headers=sauth)).json()
    assert any(a["session_id"] == session_id and a["status"] == "present" for a in my_att)

    # Чужой преподаватель не видит группу
    other = {"Authorization": f"Bearer {await _make_teacher(client)}"}
    r = await client.get(f"/scheduling/groups/{group_id}", headers=other)
    assert r.status_code == 403
