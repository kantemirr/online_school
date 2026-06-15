"""Интеграционный тест уведомлений: события → in-app, чтение, RBAC."""
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
    email = f"ntf_{uuid4().hex[:10]}@example.com"
    username = f"nt_{uuid4().hex[:8]}"
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
    sid = (await client.get("/users/me", headers={"Authorization": f"Bearer {sacc}"})).json()["id"]
    return sacc, sid


async def _make_teacher(client) -> str:
    a = await client.post("/auth/login", json={"email": "admin@codekids.ru", "password": "admin12345"})
    admin_auth = {"Authorization": f"Bearer {a.json()['access_token']}"}
    email = f"tn_{uuid4().hex[:8]}@codekids.ru"
    await client.post("/admin/users", headers=admin_auth, json={
        "email": email, "password": "teacherpass1", "role": "teacher", "full_name": "T",
    })
    return (await client.post("/auth/login", json={"email": email, "password": "teacherpass1"})).json()["access_token"]


async def test_notifications_flow(client, redis):
    sacc, student_id = await _make_student(client, redis)
    sauth = {"Authorization": f"Bearer {sacc}"}

    course_id = (await client.get("/catalog/courses", params={"q": "Python"})).json()["items"][0]["id"]
    await client.post(f"/learning/courses/{course_id}/enroll", headers=sauth)

    # Завершение первого урока → достижение → уведомление
    passage = (await client.get(f"/learning/courses/{course_id}", headers=sauth)).json()
    first_lesson_id = passage["modules"][0]["lessons"][0]["id"]
    await client.post(f"/learning/lessons/{first_lesson_id}/complete", headers=sauth)

    notes = (await client.get("/notifications", headers=sauth)).json()
    assert any(n["type"] == "achievement" for n in notes)
    count1 = (await client.get("/notifications/unread-count", headers=sauth)).json()["count"]
    assert count1 >= 1

    # Преподаватель назначает занятие группе с учеником → new_session
    tauth = {"Authorization": f"Bearer {await _make_teacher(client)}"}
    gid = (await client.post("/scheduling/groups", headers=tauth, json={"course_id": course_id, "name": "G"})).json()["id"]
    await client.post(f"/scheduling/groups/{gid}/members", headers=tauth, json={"student_id": student_id})
    await client.post(f"/scheduling/groups/{gid}/sessions", headers=tauth, json={
        "starts_at": "2026-07-01T10:00:00Z", "ends_at": "2026-07-01T11:00:00Z",
        "meeting_url": "https://meet.jit.si/x",
    })
    notes2 = (await client.get("/notifications", headers=sauth)).json()
    assert any(n["type"] == "new_session" for n in notes2)
    count2 = (await client.get("/notifications/unread-count", headers=sauth)).json()["count"]
    assert count2 > count1

    # Прочтение одного уменьшает счётчик
    first_id = notes2[0]["id"]
    await client.post(f"/notifications/{first_id}/read", headers=sauth)
    count3 = (await client.get("/notifications/unread-count", headers=sauth)).json()["count"]
    assert count3 == count2 - 1

    # read-all обнуляет
    await client.post("/notifications/read-all", headers=sauth)
    assert (await client.get("/notifications/unread-count", headers=sauth)).json()["count"] == 0

    # RBAC: чужое уведомление недоступно
    other_acc, _ = await _make_student(client, redis)
    r = await client.post(f"/notifications/{first_id}/read", headers={"Authorization": f"Bearer {other_acc}"})
    assert r.status_code == 404
