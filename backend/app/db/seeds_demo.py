"""Полноценные демонстрационные данные (идемпотентно).

Запуск: `python -m app.db.seeds_demo`

Документированные аккаунты (для входа/ВКР):
  admin@codekids.ru / admin12345         (создаётся bootstrap'ом отдельно)
  parent@codekids.ru / parent12345
  teacher@codekids.ru / teacher12345
  ребёнок: логин kid / PIN 1234

Плюс: 12 родителей (с телефонами), 4 преподавателя, 30 детей с реалистичными
данными, записи на курсы и прогресс, достижения, группы с занятиями и
посещаемостью, оплаченные абонементы — чтобы экраны всех ролей и аналитика
были наполнены.
"""
import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import hash_password, hash_pin
from app.db.enums import (
    AttendanceStatus,
    CodeVerdict,
    EnrollmentStatus,
    LessonProgressStatus,
    PaymentStatus,
    SubmissionStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    UserRole,
)
from app.db.session import SessionLocal
from app.modules.catalog.models import Assignment, Course, Lesson, Module
from app.modules.gamification import service as gamification
from app.modules.grading.models import Submission
from app.modules.learning.models import Enrollment, LessonProgress
from app.modules.payments.models import Payment, Subscription
from app.modules.scheduling.models import Attendance, Group, GroupMember, ScheduleSession
from app.modules.users.models import ParentProfile, StudentProfile, TeacherProfile, User
from app.modules.users.utils import age_group_for

# ── Справочные списки ────────────────────────────────────────────────────────
PARENTS = [
    ("parent@codekids.ru", "Демидов Олег Иванович", "+7 901 111-22-33", "parent12345"),
    ("ivanova@example.com", "Иванова Елена Сергеевна", "+7 902 234-56-78", "demo12345"),
    ("petrov@example.com", "Петров Андрей Николаевич", "+7 903 345-67-89", "demo12345"),
    ("smirnova@example.com", "Смирнова Ольга Дмитриевна", "+7 904 456-78-90", "demo12345"),
    ("kuznetsov@example.com", "Кузнецов Сергей Павлович", "+7 905 567-89-01", "demo12345"),
    ("sokolova@example.com", "Соколова Наталья Викторовна", "+7 906 678-90-12", "demo12345"),
    ("popov@example.com", "Попов Дмитрий Алексеевич", "+7 909 789-01-23", "demo12345"),
    ("lebedeva@example.com", "Лебедева Татьяна Игоревна", "+7 910 890-12-34", "demo12345"),
    ("novikov@example.com", "Новиков Михаил Юрьевич", "+7 911 901-23-45", "demo12345"),
    ("morozova@example.com", "Морозова Ирина Олеговна", "+7 912 012-34-56", "demo12345"),
    ("volkov@example.com", "Волков Артём Сергеевич", "+7 913 123-45-67", "demo12345"),
    ("zaytseva@example.com", "Зайцева Марина Петровна", "+7 914 234-56-78", "demo12345"),
]

TEACHERS = [
    ("teacher@codekids.ru", "Иванова Мария Петровна", "Python", "teacher12345"),
    ("teacher.scratch@codekids.ru", "Орлов Павел Сергеевич", "Scratch и игры", "demo12345"),
    ("teacher.web@codekids.ru", "Кравцова Анна Дмитриевна", "Веб-разработка", "demo12345"),
    ("teacher.algo@codekids.ru", "Белов Никита Андреевич", "Алгоритмы", "demo12345"),
]

# 30 детей: (ник, год рождения). Логины и PIN генерируются по индексу.
CHILD_NAMES = [
    ("Алиса", 2014), ("Максим", 2013), ("София", 2015), ("Артём", 2012), ("Мария", 2014),
    ("Иван", 2011), ("Анна", 2013), ("Дмитрий", 2012), ("Полина", 2015), ("Егор", 2014),
    ("Варвара", 2013), ("Кирилл", 2011), ("Ева", 2016), ("Михаил", 2012), ("Дарья", 2014),
    ("Никита", 2013), ("Виктория", 2015), ("Лев", 2014), ("Алёна", 2012), ("Тимофей", 2013),
    ("Ксения", 2011), ("Роман", 2012), ("Милана", 2015), ("Глеб", 2014), ("Арина", 2013),
    ("Савелий", 2012), ("Вероника", 2014), ("Матвей", 2011), ("Злата", 2015), ("Фёдор", 2013),
]


async def _get_or_create_user_with_profile(db, email, password, role, profile):
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        return existing.id
    user = User(email=email, password_hash=hash_password(password), role=role,
                is_active=True, is_email_verified=True)
    if role == UserRole.PARENT:
        user.parent_profile = profile
    elif role == UserRole.TEACHER:
        user.teacher_profile = profile
    db.add(user)
    await db.commit()
    return user.id


async def seed_demo() -> None:
    async with SessionLocal() as db:
        # ── Курсы (карта название→id, цена) ──────────────────────────────────
        course_rows = (await db.execute(select(Course.id, Course.title, Course.price))).all()
        course_ids = [cid for cid, _, _ in course_rows]
        if not course_ids:
            print("seed_demo: сначала запустите seeds_content (нет курсов)")
            return
        price_of = {cid: price for cid, _, price in course_rows}

        # ── Преподаватели ────────────────────────────────────────────────────
        teacher_ids = []
        for email, name, spec, pwd in TEACHERS:
            tid = await _get_or_create_user_with_profile(
                db, email, pwd, UserRole.TEACHER,
                TeacherProfile(full_name=name, specialization=spec),
            )
            teacher_ids.append(tid)

        # ── Родители ─────────────────────────────────────────────────────────
        parent_ids = []
        for email, name, phone, pwd in PARENTS:
            pid = await _get_or_create_user_with_profile(
                db, email, pwd, UserRole.PARENT,
                ParentProfile(full_name=name, phone=phone, consent_pdn=True),
            )
            parent_ids.append(pid)

        # ── Дети (30), распределены по родителям ─────────────────────────────
        student_ids = []
        for i, (nick, year) in enumerate(CHILD_NAMES):
            login = "kid" if i == 0 else f"kid{i + 1:02d}"
            pin = "1234" if i == 0 else f"{1000 + i}"
            existing = await db.scalar(select(StudentProfile).where(StudentProfile.login_username == login))
            if existing is not None:
                student_ids.append(existing.user_id)
                continue
            parent_id = parent_ids[i % len(parent_ids)]
            bday = date(year, (i % 12) + 1, (i % 27) + 1)
            child = User(email=None, password_hash=hash_password("disabled"),
                         role=UserRole.STUDENT, is_active=True, is_email_verified=False)
            sp = StudentProfile(
                parent_id=parent_id, nickname=nick, birth_date=bday,
                age_group=age_group_for(bday), login_username=login, pin_hash=hash_pin(pin),
                xp=50 + (i * 53) % 1500, streak=i % 13,
                last_active_date=date.today() if i % 3 else None,
            )
            child.student_profile = sp
            db.add(child)
            await db.commit()
            student_ids.append(sp.user_id)

        # ── Записи на курсы + прогресс + passed-код ──────────────────────────
        for i, sid in enumerate(student_ids):
            chosen = {course_ids[i % len(course_ids)], course_ids[(i + 3) % len(course_ids)]}
            for cid in chosen:
                if await db.scalar(select(Enrollment).where(
                    Enrollment.student_id == sid, Enrollment.course_id == cid)):
                    continue
                lessons = (await db.execute(
                    select(Lesson.id).join(Module, Module.id == Lesson.module_id)
                    .where(Module.course_id == cid)
                    .order_by(Module.order_index, Lesson.order_index)
                )).scalars().all()
                done = lessons[: max(1, (i % 3) + 1)] if lessons else []
                completed = len(done) == len(lessons) and lessons
                enr = Enrollment(
                    student_id=sid, course_id=cid,
                    status=EnrollmentStatus.COMPLETED if completed else EnrollmentStatus.ACTIVE,
                    progress_pct=round(len(done) / len(lessons) * 100, 2) if lessons else 0,
                )
                db.add(enr)
                await db.commit()
                for lid in done:
                    db.add(LessonProgress(
                        enrollment_id=enr.id, lesson_id=lid,
                        status=LessonProgressStatus.COMPLETED, score=90 + (i % 10),
                        completed_at=datetime.now(timezone.utc),
                    ))
                await db.commit()

            # Каждый третий ребёнок — успешно сдал код-задание (для достижения)
            if i % 3 == 0:
                code_aid = await db.scalar(
                    select(Assignment.id).join(Lesson, Lesson.id == Assignment.lesson_id)
                    .join(Module, Module.id == Lesson.module_id)
                    .where(Assignment.type == "code").limit(1)
                )
                if code_aid and not await db.scalar(select(Submission).where(
                    Submission.student_id == sid, Submission.assignment_id == code_aid)):
                    db.add(Submission(
                        assignment_id=code_aid, student_id=sid, code="print(int(input())**2)",
                        status=SubmissionStatus.CHECKED, verdict=CodeVerdict.PASSED, score=100,
                        result_json={"summary": {"passed": 2, "total": 2, "verdict": "passed"}, "tests": []},
                        checked_at=datetime.now(timezone.utc),
                    ))
                    await db.commit()

        # ── Группы + занятия + посещаемость ──────────────────────────────────
        now = datetime.now(timezone.utc)
        group_names = [
            "Питон-понедельник", "Scratch-старт", "Веб-мастера",
            "Алгоритмика PRO", "Юные программисты",
        ]
        for gi, gname in enumerate(group_names):
            if await db.scalar(select(Group).where(Group.name == gname)):
                continue
            tid = teacher_ids[gi % len(teacher_ids)]
            cid = course_ids[gi % len(course_ids)]
            group = Group(course_id=cid, teacher_id=tid, name=gname)
            db.add(group)
            await db.commit()
            members = student_ids[gi * 5: gi * 5 + 5]
            for sid in members:
                db.add(GroupMember(group_id=group.id, student_id=sid))
            past = ScheduleSession(group_id=group.id, teacher_id=tid,
                                   starts_at=now - timedelta(days=3, hours=-10),
                                   ends_at=now - timedelta(days=3, hours=-11),
                                   meeting_url="https://meet.jit.si/codekids-" + str(gi))
            future = ScheduleSession(group_id=group.id, teacher_id=tid,
                                     starts_at=now + timedelta(days=2, hours=10),
                                     ends_at=now + timedelta(days=2, hours=11),
                                     meeting_url="https://meet.jit.si/codekids-" + str(gi))
            db.add_all([past, future])
            await db.commit()
            statuses = [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.EXCUSED]
            for mi, sid in enumerate(members):
                db.add(Attendance(session_id=past.id, student_id=sid, status=statuses[mi % 3]))
            await db.commit()

        # ── Платежи: у части родителей активные абонементы ───────────────────
        plans = [SubscriptionPlan.MONTHLY, SubscriptionPlan.ANNUAL, SubscriptionPlan.COURSE]
        amounts = {SubscriptionPlan.MONTHLY: "990.00", SubscriptionPlan.ANNUAL: "9900.00"}
        for pi, parent_id in enumerate(parent_ids[:7]):
            if await db.scalar(select(Subscription).where(Subscription.parent_id == parent_id)):
                continue
            plan = plans[pi % 3]
            cid = course_ids[pi % len(course_ids)] if plan == SubscriptionPlan.COURSE else None
            amount = amounts.get(plan) or str(price_of.get(cid, "990.00"))
            days = 30 if plan == SubscriptionPlan.MONTHLY else 365
            sub = Subscription(parent_id=parent_id, course_id=cid, plan=plan,
                               period_start=date.today(), period_end=date.today() + timedelta(days=days),
                               status=SubscriptionStatus.ACTIVE)
            db.add(sub)
            await db.commit()
            pay = Payment(subscription_id=sub.id, amount=amount, status=PaymentStatus.PAID,
                          paid_at=now)
            db.add(pay)
            await db.commit()
            pay.receipt_no = f"RC-{pay.id:08d}"
            await db.commit()

        # ── Достижения + пересчёт лидербордов ────────────────────────────────
        for sid in student_ids:
            await gamification.evaluate_achievements(db, sid)
        await gamification.recalc_leaderboards(db)

        print(
            f"seed_demo готово: преподавателей={len(teacher_ids)}, родителей={len(parent_ids)}, "
            f"детей={len(student_ids)}, групп={len(group_names)}.\n"
            "  Креды: parent@codekids.ru/parent12345, teacher@codekids.ru/teacher12345, ребёнок kid/1234"
        )


if __name__ == "__main__":
    asyncio.run(seed_demo())
