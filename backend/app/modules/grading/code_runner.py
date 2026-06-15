"""Агрегация результатов прогона кода по тест-кейсам (чистая логика).

Формирует вердикт и баллы из результатов песочницы и строит БЕЗОПАСНЫЙ фидбэк:
видимые тесты раскрывают вход/ожидание/получено, скрытые — только pass/fail.
Эталонное решение не фигурирует нигде.
"""
from app.db.enums import CodeVerdict


def evaluate_one(expected_stdout: str, sandbox_result: dict) -> tuple[bool, str]:
    """Прошёл ли тест. Возвращает (passed, got)."""
    got = (sandbox_result.get("stdout") or "").strip()
    ok = (
        not sandbox_result.get("timed_out")
        and sandbox_result.get("exit_code") == 0
        and got == (expected_stdout or "").strip()
    )
    return ok, got


def aggregate(results: list[dict], max_score: int) -> dict:
    """results — список {test_no, weight, passed, hidden, stdin, expected, got, stderr, timed_out}.

    Возвращает вердикт, баллы и безопасный result_json.
    """
    total = len(results)

    # Деградация: песочница недоступна (Docker/воркер) — не выдаём ложный «failed»,
    # урок не закрываем, показываем дружелюбное «попробуйте позже».
    if total and all(r.get("infra_error") for r in results):
        return {
            "verdict": None,
            "score": 0,
            "result_json": {
                "summary": {"passed": 0, "total": total, "verdict": None},
                "tests": [],
                "stderr": "",
                "unavailable": True,
            },
            "feedback": "Автопроверка кода временно недоступна, попробуйте позже.",
        }
    total_weight = sum(r["weight"] for r in results) or 1
    passed_weight = sum(r["weight"] for r in results if r["passed"])
    passed_count = sum(1 for r in results if r["passed"])
    score = round(passed_weight / total_weight * max_score)

    if total and passed_count == total:
        verdict = CodeVerdict.PASSED
    elif passed_count == 0:
        verdict = CodeVerdict.FAILED
    else:
        verdict = CodeVerdict.PARTIAL

    safe_tests = []
    first_stderr = ""
    for r in results:
        if r.get("stderr") and not first_stderr:
            first_stderr = r["stderr"]
        item = {"test_no": r["test_no"], "passed": r["passed"], "hidden": r["hidden"]}
        if not r["hidden"]:
            item.update({
                "stdin": r.get("stdin"),
                "expected": r.get("expected"),
                "got": r.get("got"),
            })
        safe_tests.append(item)

    return {
        "verdict": verdict,
        "score": score,
        "result_json": {
            "summary": {"passed": passed_count, "total": total, "verdict": verdict.value},
            "tests": safe_tests,
            "stderr": first_stderr[:2000],
        },
        "feedback": f"Пройдено {passed_count} из {total} тестов.",
    }
