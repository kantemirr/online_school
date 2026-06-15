"""Фоновая проверка кода в песочнице (вызывается ARQ-задачей code_check)."""
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.enums import CodeVerdict, SubmissionStatus
from app.db.session import SessionLocal
from app.modules.catalog.models import Assignment, Lesson, Module
from app.modules.grading import repository as repo
from app.modules.grading.code_runner import aggregate, evaluate_one
from app.modules.grading.models import Submission
from app.modules.grading.sandbox import run_in_sandbox
from app.modules.learning import repository as learning_repo
from app.modules.learning import service as learning

settings = get_settings()
logger = get_logger(__name__)


async def run_code_check(submission_id: int) -> None:
    async with SessionLocal() as db:
        submission = await db.get(Submission, submission_id)
        if submission is None or submission.code is None:
            return
        assignment = await db.get(Assignment, submission.assignment_id)

        submission.status = SubmissionStatus.RUNNING
        await db.commit()

        tests = await repo.get_code_tests(db, assignment.id)
        results = []
        for index, test in enumerate(tests, start=1):
            sandbox_result = await run_in_sandbox(
                submission.code, test.stdin or "", settings.SANDBOX_TIMEOUT_SEC
            )
            passed, got = evaluate_one(test.expected_stdout, sandbox_result)
            results.append({
                "test_no": index, "weight": test.weight, "passed": passed,
                "hidden": test.is_hidden, "stdin": test.stdin,
                "expected": test.expected_stdout, "got": got,
                "stderr": sandbox_result.get("stderr", ""),
                "timed_out": sandbox_result.get("timed_out", False),
                "infra_error": sandbox_result.get("infra_error", False),
            })

        if not tests:
            agg = {
                "verdict": CodeVerdict.FAILED, "score": 0,
                "result_json": {"summary": {"passed": 0, "total": 0}, "tests": [], "stderr": ""},
                "feedback": "У задания нет тест-кейсов.",
            }
        else:
            agg = aggregate(results, assignment.max_score)

        submission.status = SubmissionStatus.CHECKED
        submission.verdict = agg["verdict"]
        submission.score = agg["score"]
        submission.result_json = agg["result_json"]
        submission.feedback = agg["feedback"]
        submission.checked_at = datetime.now(timezone.utc)
        await db.commit()

        if agg["verdict"] == CodeVerdict.PASSED:
            module = await db.get(Module, (await db.get(Lesson, assignment.lesson_id)).module_id)
            enrollment = await learning_repo.get_enrollment(db, submission.student_id, module.course_id)
            if enrollment is not None:
                await learning.mark_lesson_completed(db, enrollment, assignment.lesson_id, agg["score"])

        # Уведомление ученику (+ email родителю). verdict=None — деградация песочницы.
        from app.modules.notifications import service as notifications
        verdict_str = agg["verdict"].value if agg["verdict"] is not None else "unavailable"
        await notifications.notify_work_checked(
            db, submission.student_id, submission.id, verdict_str
        )

        logger.info("code_check done: submission=%s verdict=%s", submission_id, agg["verdict"])
