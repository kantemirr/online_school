"""Прикладная логика админ-панели: пользователи, реестры, справочники."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.redis import redis_client
from app.core.security import hash_password
from app.db.enums import (
    AgeGroup,
    AttendanceStatus,
    CourseLevel,
    CourseTrack,
    NotificationType,
    PaymentStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    UserRole,
)
from app.modules.admin import repository as repo
from app.modules.admin.audit import record_audit
from app.modules.admin.schemas import (
    AdminAuditListOut,
    AdminAuditOut,
    AdminGroupListOut,
    AdminGroupOut,
    AdminPaymentListOut,
    AdminPaymentOut,
    AdminUserListOut,
    AdminUserOut,
    ReferenceItem,
    ReferenceOut,
    UpdateUserIn,
)
from app.modules.auth.tokens import revoke_all_refresh
from app.modules.users.models import TeacherProfile, User

# Роли «персонала» — только между ними допускается смена роли через панель.
_STAFF_ROLES = {UserRole.TEACHER, UserRole.ADMIN}

_REASON_MESSAGES = {
    "cannot_modify_self": "Нельзя заблокировать или понизить собственную учётную запись",
    "last_admin": "Нельзя заблокировать или понизить последнего активного администратора",
    "role_change_unsupported": "Смена роли допустима только между «преподаватель» и «администратор»",
}


def protected_change_reason(
    *,
    target_id: int,
    actor_id: int,
    target_role: UserRole,
    target_active: bool,
    new_role: UserRole | None,
    new_active: bool | None,
    active_admins: int,
) -> str | None:
    """Можно ли применить изменение? None — можно; иначе код-причина (для 409).

    Чистая функция (без БД) — покрыта unit-тестами. Защищает платформу от
    самоблокировки администратора и от потери последнего активного админа.
    """
    deactivating = new_active is False and target_active is True
    demoting = (
        target_role == UserRole.ADMIN
        and new_role is not None
        and new_role != UserRole.ADMIN
    )
    # Запрет менять самого себя в сторону понижения/блокировки.
    if (deactivating or demoting) and target_id == actor_id:
        return "cannot_modify_self"
    # Нельзя «увести» последнего активного администратора.
    losing_active_admin = (
        target_role == UserRole.ADMIN and target_active and (deactivating or demoting)
    )
    if losing_active_admin and active_admins <= 1:
        return "last_admin"
    # Смена роли — только в пределах персонала (profile-coupled роли не трогаем).
    if new_role is not None and new_role != target_role:
        if target_role not in _STAFF_ROLES or new_role not in _STAFF_ROLES:
            return "role_change_unsupported"
    return None


def _user_out(user: User, display_name: str | None) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        display_name=display_name,
        created_at=user.created_at,
    )


# ── Пользователи ─────────────────────────────────────────────────────────────
async def list_users(
    db: AsyncSession,
    *,
    role: UserRole | None,
    is_active: bool | None,
    q: str | None,
    page: int,
    size: int,
) -> AdminUserListOut:
    rows, total = await repo.list_users(
        db, role=role, is_active=is_active, q=q, page=page, size=size
    )
    return AdminUserListOut(
        items=[_user_out(u, name) for u, name in rows],
        total=total,
        page=page,
        size=size,
    )


async def get_user(db: AsyncSession, user_id: int) -> AdminUserOut:
    row = await repo.get_user_with_name(db, user_id)
    if row is None:
        raise NotFoundError("Пользователь не найден", code="user_not_found")
    return _user_out(*row)


async def update_user(
    db: AsyncSession, actor: User, user_id: int, data: UpdateUserIn
) -> AdminUserOut:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден", code="user_not_found")

    if data.is_active is None and data.role is None:
        return await get_user(db, user_id)  # пустое тело — no-op

    active_admins = await repo.count_active_admins(db)
    reason = protected_change_reason(
        target_id=user.id,
        actor_id=actor.id,
        target_role=user.role,
        target_active=user.is_active,
        new_role=data.role,
        new_active=data.is_active,
        active_admins=active_admins,
    )
    if reason is not None:
        raise ConflictError(_REASON_MESSAGES[reason], code=reason)

    if data.role is not None and data.role != user.role:
        user.role = data.role
        # admin → teacher без профиля: создаём минимальный профиль преподавателя.
        if data.role == UserRole.TEACHER and await db.get(TeacherProfile, user.id) is None:
            db.add(
                TeacherProfile(
                    user_id=user.id, full_name=user.email or f"teacher#{user.id}"
                )
            )
    if data.is_active is not None:
        user.is_active = data.is_active

    await db.commit()
    # Блокировка вступает в силу сразу: отзываем все refresh пользователя.
    if data.is_active is False:
        await revoke_all_refresh(redis_client, user.id)
    await record_audit(
        db, actor, "user_update", target=f"user#{user_id}",
        meta={"is_active": data.is_active, "role": data.role},
    )
    return await get_user(db, user_id)


async def reset_password(db: AsyncSession, actor: User, user_id: int, new_password: str) -> None:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден", code="user_not_found")
    user.password_hash = hash_password(new_password)
    await db.commit()
    await revoke_all_refresh(redis_client, user.id)
    await record_audit(db, actor, "password_reset", target=f"user#{user_id}")


async def list_audit(db: AsyncSession, *, page: int, size: int) -> AdminAuditListOut:
    rows, total = await repo.list_audit(db, page=page, size=size)
    return AdminAuditListOut(
        items=[
            AdminAuditOut(
                id=a.id, actor_email=a.actor_email, action=a.action,
                target=a.target, created_at=a.created_at,
            )
            for a in rows
        ],
        total=total, page=page, size=size,
    )


# ── Реестры ──────────────────────────────────────────────────────────────────
async def list_payments(
    db: AsyncSession, *, status: PaymentStatus | None, page: int, size: int
) -> AdminPaymentListOut:
    rows, total = await repo.list_payments(db, status=status, page=page, size=size)
    return AdminPaymentListOut(
        items=[
            AdminPaymentOut(
                id=p.id,
                payer_email=email,
                plan=plan,
                amount=p.amount,
                status=p.status,
                receipt_no=p.receipt_no,
                paid_at=p.paid_at,
            )
            for p, plan, email in rows
        ],
        total=total,
        page=page,
        size=size,
    )


async def list_groups(
    db: AsyncSession, *, page: int, size: int
) -> AdminGroupListOut:
    rows, total = await repo.list_groups(db, page=page, size=size)
    return AdminGroupListOut(
        items=[
            AdminGroupOut(
                id=g.id,
                name=g.name,
                teacher_name=teacher_name,
                course_title=course_title,
                members=members,
                sessions=sessions,
            )
            for g, teacher_name, course_title, members, sessions in rows
        ],
        total=total,
        page=page,
        size=size,
    )


# ── Справочники ──────────────────────────────────────────────────────────────
_LABELS: dict[str, dict[str, str]] = {
    "roles": {
        UserRole.STUDENT: "Ученик",
        UserRole.PARENT: "Родитель",
        UserRole.TEACHER: "Преподаватель",
        UserRole.ADMIN: "Администратор",
    },
    "tracks": {
        CourseTrack.SCRATCH: "Scratch",
        CourseTrack.PYTHON: "Python",
        CourseTrack.WEB: "Веб-разработка",
        CourseTrack.GAMEDEV: "Разработка игр",
        CourseTrack.ALGORITHMS: "Алгоритмы",
    },
    "levels": {
        CourseLevel.BEGINNER: "Начальный",
        CourseLevel.INTERMEDIATE: "Средний",
        CourseLevel.ADVANCED: "Продвинутый",
    },
    "age_groups": {
        AgeGroup.JUNIOR: "8–10 лет",
        AgeGroup.MIDDLE: "11–12 лет",
        AgeGroup.SENIOR: "13–14 лет",
    },
    "subscription_plans": {
        SubscriptionPlan.COURSE: "Доступ к курсу",
        SubscriptionPlan.MONTHLY: "Месячная подписка",
        SubscriptionPlan.ANNUAL: "Годовая подписка",
    },
    "subscription_statuses": {
        SubscriptionStatus.PENDING: "Ожидает оплаты",
        SubscriptionStatus.ACTIVE: "Активен",
        SubscriptionStatus.EXPIRED: "Истёк",
        SubscriptionStatus.CANCELLED: "Отменён",
    },
    "payment_statuses": {
        PaymentStatus.PENDING: "Ожидает",
        PaymentStatus.PAID: "Оплачен",
        PaymentStatus.FAILED: "Ошибка",
        PaymentStatus.REFUNDED: "Возврат",
    },
    "attendance_statuses": {
        AttendanceStatus.PRESENT: "Присутствовал",
        AttendanceStatus.ABSENT: "Отсутствовал",
        AttendanceStatus.EXCUSED: "Уважительная причина",
    },
    "notification_types": {
        NotificationType.WORK_CHECKED: "Работа проверена",
        NotificationType.NEW_SESSION: "Новое занятие",
        NotificationType.DEADLINE: "Дедлайн",
        NotificationType.ACHIEVEMENT: "Достижение",
        NotificationType.PAYMENT_STATUS: "Статус оплаты",
    },
}


def reference_data() -> ReferenceOut:
    """Значения перечислений с русскими подписями — для выпадающих списков фронта."""
    return ReferenceOut(
        sections={
            section: [
                ReferenceItem(value=str(value), label=label)
                for value, label in items.items()
            ]
            for section, items in _LABELS.items()
        }
    )
