"""ИИ-подсказки по ошибкам в коде ученика.

Принцип безопасности: в модель уходит ТОЛЬКО код ученика + его stderr + номера
непройденных видимых тестов. Эталонное решение и ожидаемые выводы скрытых
тестов НЕ передаются — подсказка не раскрывает ответ.

Провайдер — Anthropic (Claude Haiku 4.5). Без ANTHROPIC_API_KEY — авто-фолбэк
на эвристику по типу ошибки в stderr.
"""
import re

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# (паттерн в stderr → дружелюбная подсказка), без готового решения
_HEURISTICS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"SyntaxError"), "Похоже, в коде синтаксическая ошибка — проверь скобки, двоеточия и кавычки."),
    (re.compile(r"IndentationError|TabError"), "Проверь отступы: в Python тело цикла и функции сдвигается вправо одинаково."),
    (re.compile(r"NameError"), "Используется имя, которое не объявлено. Нет ли опечатки в названии переменной?"),
    (re.compile(r"TypeError"), "Операция применяется к неподходящему типу. Может, строку нужно превратить в число через int()?"),
    (re.compile(r"ValueError"), "Значение не подходит для операции — например, int() от нечисловой строки."),
    (re.compile(r"ZeroDivisionError"), "Деление на ноль — проверь делитель перед делением."),
    (re.compile(r"IndexError"), "Обращение к несуществующему элементу списка — проверь границы индексов."),
    (re.compile(r"KeyError"), "В словаре нет такого ключа — проверь имена ключей."),
    (re.compile(r"EOFError"), "Программа просит ввод, которого нет. Проверь, сколько раз вызываешь input()."),
]


def heuristic_hint(stderr: str, has_failures: bool) -> str:
    for pattern, message in _HEURISTICS:
        if pattern.search(stderr or ""):
            return message
    if has_failures:
        return ("Программа запускается, но выводит не то, что ждут. Сверь формат вывода "
                "с примером: пробелы, перевод строки, тип данных.")
    return "Перечитай условие и пример входных и выходных данных — что именно нужно вывести?"


async def _ai_hint(code: str, stderr: str, failed_visible: list[int]) -> str | None:
    if not settings.ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        system = (
            "Ты — дружелюбный помощник для детей 8–14 лет, которые учат Python. "
            "Дай ОДНУ короткую подсказку (1–3 предложения) на русском, которая поможет "
            "понять ошибку. СТРОГО: не давай готовый или исправленный код, не пиши "
            "правильный ответ. Только направление — на какой концепт или строку посмотреть."
        )
        user = (
            f"Код ученика:\n```python\n{code[:4000]}\n```\n\n"
            f"Сообщение об ошибке (stderr):\n{(stderr or '(нет)')[:1500]}\n\n"
            f"Не прошли видимые тесты с номерами: {failed_visible or 'нет данных'}"
        )
        resp = await client.messages.create(
            model=settings.AI_HINT_MODEL,
            max_tokens=200,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        return text or None
    except Exception as exc:  # noqa: BLE001 — деградация на эвристику
        logger.warning("ai hint failed, falling back: %s", exc)
        return None


async def generate_hint(
    code: str, stderr: str, failed_visible: list[int], has_failures: bool
) -> tuple[str, str]:
    """Возвращает (текст_подсказки, источник: "ai"|"heuristic")."""
    ai = await _ai_hint(code, stderr, failed_visible)
    if ai:
        return ai, "ai"
    return heuristic_hint(stderr, has_failures), "heuristic"
