"""Unit-тесты админ-панели: защита изменений учётной записи (без инфры)."""
from app.db.enums import UserRole
from app.modules.admin.service import protected_change_reason


def _check(**over):
    base = dict(
        target_id=2,
        actor_id=1,
        target_role=UserRole.PARENT,
        target_active=True,
        new_role=None,
        new_active=None,
        active_admins=5,
    )
    base.update(over)
    return protected_change_reason(**base)


def test_cannot_deactivate_self():
    assert _check(target_id=1, target_role=UserRole.ADMIN, new_active=False) == "cannot_modify_self"


def test_cannot_demote_self():
    assert _check(target_id=1, target_role=UserRole.ADMIN, new_role=UserRole.TEACHER) == "cannot_modify_self"


def test_last_active_admin_blocked():
    assert _check(target_role=UserRole.ADMIN, new_active=False, active_admins=1) == "last_admin"


def test_role_change_parent_to_admin_unsupported():
    assert _check(target_role=UserRole.PARENT, new_role=UserRole.ADMIN) == "role_change_unsupported"


def test_role_change_admin_to_parent_unsupported():
    assert _check(target_id=2, target_role=UserRole.ADMIN, new_role=UserRole.PARENT, active_admins=5) == "role_change_unsupported"


def test_teacher_to_admin_allowed():
    assert _check(target_role=UserRole.TEACHER, new_role=UserRole.ADMIN) is None


def test_deactivate_non_admin_allowed():
    assert _check(target_role=UserRole.PARENT, new_active=False) is None


def test_inactive_admin_demote_not_last():
    # понижение НЕактивного админа не уменьшает число активных → не блокируется
    assert _check(target_role=UserRole.ADMIN, target_active=False,
                  new_role=UserRole.TEACHER, active_admins=1) is None


def test_empty_change_ok():
    assert _check() is None
