"""Чистая логика автопроверки квизов (без БД).

Конвенции данных вопроса:
  single / multiple — options_json = [варианты], correct_json = [индексы];
  matching          — options_json = {"left":[...],"right":[...]},
                      correct_json = [[left_idx, right_idx], ...].
Ответ ученика: для single/multiple — список индексов; для matching — список пар.
"""
from typing import Any

from app.db.enums import QuestionKind

PASS_RATIO = 0.6  # доля верных для зачёта задания


def is_question_correct(kind: QuestionKind, correct_json: Any, answer: Any) -> bool:
    if kind in (QuestionKind.SINGLE, QuestionKind.MULTIPLE):
        return set(answer or []) == set(correct_json or [])
    if kind == QuestionKind.MATCHING:
        norm = lambda pairs: {tuple(p) for p in (pairs or [])}
        return norm(answer) == norm(correct_json)
    return False


def grade_quiz(questions: list, answers: dict) -> dict:
    """questions — объекты с .id/.kind/.correct_json; answers — {qid: ответ}.

    Возвращает {correct, total, ratio, passed, wrong_question_ids}.
    """
    total = len(questions)
    correct = 0
    wrong: list[int] = []
    for q in questions:
        ans = answers.get(str(q.id), answers.get(q.id))
        if is_question_correct(q.kind, q.correct_json, ans):
            correct += 1
        else:
            wrong.append(q.id)
    ratio = (correct / total) if total else 0.0
    return {
        "correct": correct,
        "total": total,
        "ratio": round(ratio, 4),
        "passed": ratio >= PASS_RATIO,
        "wrong_question_ids": wrong,
    }
