"""Unit-тесты грейдинга (без БД/Docker/сети)."""
from dataclasses import dataclass

from app.db.enums import CodeVerdict, QuestionKind
from app.modules.grading.code_runner import aggregate, evaluate_one
from app.modules.grading.hints import heuristic_hint
from app.modules.grading.quiz import grade_quiz, is_question_correct


@dataclass
class Q:
    id: int
    kind: QuestionKind
    correct_json: object


# ── Квиз ─────────────────────────────────────────────────────────────────────
def test_single_choice():
    assert is_question_correct(QuestionKind.SINGLE, [0], [0])
    assert not is_question_correct(QuestionKind.SINGLE, [0], [1])


def test_multiple_choice_order_independent():
    assert is_question_correct(QuestionKind.MULTIPLE, [0, 2], [2, 0])
    assert not is_question_correct(QuestionKind.MULTIPLE, [0, 2], [0])


def test_matching():
    assert is_question_correct(QuestionKind.MATCHING, [[0, 1], [1, 0]], [[1, 0], [0, 1]])
    assert not is_question_correct(QuestionKind.MATCHING, [[0, 1]], [[0, 0]])


def test_grade_quiz_pass_threshold():
    questions = [
        Q(1, QuestionKind.SINGLE, [0]),
        Q(2, QuestionKind.SINGLE, [1]),
        Q(3, QuestionKind.SINGLE, [2]),
    ]
    res = grade_quiz(questions, {"1": [0], "2": [1], "3": [9]})  # 2 из 3
    assert res["correct"] == 2 and res["total"] == 3
    assert res["passed"] is True  # 0.67 >= 0.6
    assert res["wrong_question_ids"] == [3]

    res2 = grade_quiz(questions, {"1": [0]})  # 1 из 3 → 0.33
    assert res2["passed"] is False


# ── Агрегация вердикта кода + безопасный фидбэк ──────────────────────────────
def _result(no, passed, hidden, weight=1):
    return {"test_no": no, "weight": weight, "passed": passed, "hidden": hidden,
            "stdin": "5", "expected": "25", "got": "25" if passed else "0", "stderr": ""}


def test_aggregate_passed():
    agg = aggregate([_result(1, True, False), _result(2, True, True)], max_score=100)
    assert agg["verdict"] == CodeVerdict.PASSED and agg["score"] == 100


def test_aggregate_partial_and_safe_feedback():
    agg = aggregate([_result(1, True, False), _result(2, False, True)], max_score=100)
    assert agg["verdict"] == CodeVerdict.PARTIAL and agg["score"] == 50
    tests = agg["result_json"]["tests"]
    visible = next(t for t in tests if t["test_no"] == 1)
    hidden = next(t for t in tests if t["test_no"] == 2)
    assert "expected" in visible              # видимый тест раскрывает детали
    assert "expected" not in hidden           # скрытый — только pass/fail
    assert hidden["passed"] is False


def test_aggregate_failed():
    agg = aggregate([_result(1, False, False)], max_score=100)
    assert agg["verdict"] == CodeVerdict.FAILED and agg["score"] == 0


def test_aggregate_sandbox_unavailable_degrades():
    # Все прогоны — infra_error (Docker/воркер недоступны) → деградация, не «failed»
    bad = {"test_no": 1, "weight": 1, "passed": False, "hidden": False, "stdin": "5",
           "expected": "25", "got": "", "stderr": "Песочница недоступна", "infra_error": True}
    agg = aggregate([bad, {**bad, "test_no": 2}], max_score=100)
    assert agg["verdict"] is None
    assert agg["score"] == 0
    assert agg["result_json"]["unavailable"] is True
    assert "недоступна" in agg["feedback"].lower()


def test_evaluate_one_trims_and_checks_exit():
    ok, got = evaluate_one("25", {"stdout": "25\n", "exit_code": 0, "timed_out": False})
    assert ok and got == "25"
    bad, _ = evaluate_one("25", {"stdout": "25", "exit_code": 1, "timed_out": False})
    assert not bad


# ── Эвристика подсказок ──────────────────────────────────────────────────────
def test_heuristic_detects_error_types():
    assert "отступ" in heuristic_hint("IndentationError: unexpected indent", True).lower()
    assert "ноль" in heuristic_hint("ZeroDivisionError: division by zero", True).lower()
    # неверный вывод без краша
    assert "формат" in heuristic_hint("", True).lower()
