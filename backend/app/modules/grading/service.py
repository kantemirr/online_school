"""Логика заданий и проверки: квизы, код (очередь), проекты, подсказки, ревью."""
import os
from datetime import datetime, timezone

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from sqlalchemy import select

from app.core.queue import enqueue
from app.db.enums import AssignmentType, CodeVerdict, SubmissionStatus, UserRole
from app.modules.auth.ratelimit import enforce_rate_limit
from app.modules.catalog.models import Assignment, Lesson, Module
from app.modules.grading import quiz, repository as repo
from app.modules.grading.hints import generate_hint
from app.modules.grading.models import Submission
from app.modules.grading.schemas import (
    AssignmentForSolveOut,
    CodeExampleOut,
    GradingQueueItem,
    HintOut,
    QuestionForSolveOut,
    ReviewIn,
    SubmissionOut,
)
from app.modules.learning import repository as learning_repo
from app.modules.learning import service as learning
from app.modules.users.models import StudentProfile, User

settings = get_settings()


def _submission_out(s: Submission) -> SubmissionOut:
    return SubmissionOut(
        id=s.id, assignment_id=s.assignment_id, status=s.status, verdict=s.verdict,
        score=s.score, feedback=s.feedback, result_json=s.result_json,
        created_at=s.created_at, checked_at=s.checked_at,
    )


async def _course_id_of_lesson(db: AsyncSession, lesson_id: int) -> int:
    lesson = await db.get(Lesson, lesson_id)
    module = await db.get(Module, lesson.module_id)
    return module.course_id


# ── Получение задания для решения ────────────────────────────────────────────
async def get_assignment_for_solve(db: AsyncSession, student: User, assignment_id: int) -> AssignmentForSolveOut:
    assignment = await repo.get_assignment(db, assignment_id)
    if assignment is None:
        raise NotFoundError("Задание не найдено", code="assignment_not_found")
    await learning.ensure_lesson_unlocked(db, student.id, assignment.lesson_id)

    questions = [
        QuestionForSolveOut(id=q.id, text=q.text, kind=q.kind, options=q.options_json)
        for q in await repo.get_questions(db, assignment_id)
    ]
    examples = [
        CodeExampleOut(stdin=t.stdin, expected_stdout=t.expected_stdout)
        for t in await repo.get_code_tests(db, assignment_id)
        if not t.is_hidden  # только видимые тесты — как примеры
    ]
    return AssignmentForSolveOut(
        id=assignment.id, type=assignment.type, title=assignment.title,
        max_score=assignment.max_score, due_at=assignment.due_at,
        questions=questions, examples=examples,
    )


# ── Квиз (мгновенная автопроверка) ───────────────────────────────────────────
async def submit_quiz(db: AsyncSession, student: User, assignment_id: int, answers: dict) -> SubmissionOut:
    assignment = await repo.get_assignment(db, assignment_id)
    if assignment is None or assignment.type != AssignmentType.QUIZ:
        raise NotFoundError("Квиз не найден", code="quiz_not_found")
    enrollment = await learning.ensure_lesson_unlocked(db, student.id, assignment.lesson_id)

    questions = await repo.get_questions(db, assignment_id)
    result = quiz.grade_quiz(questions, answers)
    score = round(result["ratio"] * assignment.max_score)

    submission = Submission(
        assignment_id=assignment_id, student_id=student.id, payload_json=answers,
        status=SubmissionStatus.CHECKED, score=score,
        feedback=f"Верно {result['correct']} из {result['total']}.",
        result_json={"correct": result["correct"], "total": result["total"],
                     "wrong_question_ids": result["wrong_question_ids"], "passed": result["passed"]},
        checked_at=datetime.now(timezone.utc),
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    if result["passed"]:
        await learning.mark_lesson_completed(db, enrollment, assignment.lesson_id, score)
    return _submission_out(submission)


# ── Код (асинхронно через песочницу) ─────────────────────────────────────────
async def submit_code(db: AsyncSession, student: User, assignment_id: int, code: str) -> SubmissionOut:
    assignment = await repo.get_assignment(db, assignment_id)
    if assignment is None or assignment.type != AssignmentType.CODE:
        raise NotFoundError("Код-задание не найдено", code="code_assignment_not_found")
    await learning.ensure_lesson_unlocked(db, student.id, assignment.lesson_id)

    submission = Submission(
        assignment_id=assignment_id, student_id=student.id, code=code,
        status=SubmissionStatus.QUEUED,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    await enqueue("code_check", submission.id)
    return _submission_out(submission)


# ── Проект (ручная проверка) ─────────────────────────────────────────────────
async def submit_project(
    db: AsyncSession, student: User, assignment_id: int, *,
    filename: str | None = None, content: bytes | None = None, link: str | None = None,
) -> SubmissionOut:
    assignment = await repo.get_assignment(db, assignment_id)
    if assignment is None or assignment.type != AssignmentType.PROJECT:
        raise NotFoundError("Проектное задание не найдено", code="project_not_found")
    await learning.ensure_lesson_unlocked(db, student.id, assignment.lesson_id)

    submission = Submission(
        assignment_id=assignment_id, student_id=student.id,
        status=SubmissionStatus.PENDING_REVIEW, file_url=link,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    if content is not None and filename:
        safe_name = os.path.basename(filename) or "project.zip"
        folder = os.path.join(settings.UPLOADS_DIR, str(submission.id))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, safe_name)
        with open(path, "wb") as fh:
            fh.write(content)
        submission.file_url = path
        await db.commit()
        await db.refresh(submission)

    return _submission_out(submission)


# ── Опрос результата ─────────────────────────────────────────────────────────
async def get_submission(db: AsyncSession, user: User, submission_id: int) -> SubmissionOut:
    submission = await db.get(Submission, submission_id)
    if submission is None:
        raise NotFoundError("Отправка не найдена", code="submission_not_found")
    if user.role == UserRole.STUDENT and submission.student_id != user.id:
        raise PermissionDeniedError("Чужая отправка", code="not_owner")
    return _submission_out(submission)


# ── ИИ-подсказка ─────────────────────────────────────────────────────────────
async def request_hint(db: AsyncSession, redis: aioredis.Redis, student: User, submission_id: int) -> HintOut:
    await enforce_rate_limit(
        redis, "hint", str(student.id), limit=settings.AI_HINT_RATE_LIMIT, window_sec=3600
    )
    submission = await db.get(Submission, submission_id)
    if submission is None or submission.student_id != student.id:
        raise NotFoundError("Отправка не найдена", code="submission_not_found")
    if submission.code is None or submission.verdict == CodeVerdict.PASSED:
        raise ConflictError("Подсказка доступна для код-задания с ошибкой", code="hint_not_applicable")

    rj = submission.result_json or {}
    stderr = rj.get("stderr", "")
    failed_visible = [
        t["test_no"] for t in rj.get("tests", [])
        if not t.get("passed") and not t.get("hidden")
    ]
    hint, source = await generate_hint(
        submission.code, stderr, failed_visible, has_failures=submission.verdict != CodeVerdict.PASSED
    )
    return HintOut(hint=hint, source=source)


# ── Ручная проверка проектов (преподаватель) ─────────────────────────────────
async def list_queue(db: AsyncSession) -> list[GradingQueueItem]:
    subs = await repo.pending_review_queue(db)
    if not subs:
        return []
    student_ids = list({s.student_id for s in subs})
    assignment_ids = list({s.assignment_id for s in subs})
    nick_rows = await db.execute(
        select(StudentProfile.user_id, StudentProfile.nickname).where(
            StudentProfile.user_id.in_(student_ids)
        )
    )
    nicks = {uid: nick for uid, nick in nick_rows.all()}
    title_rows = await db.execute(
        select(Assignment.id, Assignment.title).where(Assignment.id.in_(assignment_ids))
    )
    titles = {aid: title for aid, title in title_rows.all()}
    return [
        GradingQueueItem(
            submission_id=s.id, assignment_id=s.assignment_id, student_id=s.student_id,
            nickname=nicks.get(s.student_id), assignment_title=titles.get(s.assignment_id, ""),
            file_url=s.file_url, created_at=s.created_at,
        )
        for s in subs
    ]


async def review_project(db: AsyncSession, teacher: User, submission_id: int, data: ReviewIn) -> SubmissionOut:
    submission = await db.get(Submission, submission_id)
    if submission is None:
        raise NotFoundError("Отправка не найдена", code="submission_not_found")

    submission.score = data.score
    submission.feedback = data.feedback
    submission.checked_by = teacher.id
    submission.checked_at = datetime.now(timezone.utc)
    submission.status = (
        SubmissionStatus.REVIEWED if data.status == "reviewed" else SubmissionStatus.NEEDS_REVISION
    )
    await db.commit()
    await db.refresh(submission)

    if submission.status == SubmissionStatus.REVIEWED:
        assignment = await repo.get_assignment(db, submission.assignment_id)
        course_id = await _course_id_of_lesson(db, assignment.lesson_id)
        enrollment = await learning_repo.get_enrollment(db, submission.student_id, course_id)
        if enrollment is not None:
            await learning.mark_lesson_completed(db, enrollment, assignment.lesson_id, data.score)

    # Уведомление ученику (+ email родителю)
    from app.modules.notifications import service as notifications
    await notifications.notify_work_checked(
        db, submission.student_id, submission.id, submission.status.value
    )

    return _submission_out(submission)
