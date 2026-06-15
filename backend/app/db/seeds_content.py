"""Сид демонстрационного контента каталога.

Запуск: `python -m app.db.seeds_content`
Идемпотентно: если демо-курс с известным названием уже есть — пропускает.
Наполняет каталог материалом для Этапов 4-5 и скриншотов ВКР.
"""
import asyncio

from sqlalchemy import select

from app.db.enums import (
    AssignmentType,
    CourseLevel,
    CourseTrack,
    QuestionKind,
)
from app.db.session import SessionLocal
from app.modules.catalog.models import (
    Assignment,
    CodeTest,
    Course,
    Lesson,
    Module,
    Question,
)

DEMO_TITLE = "Python с нуля для детей"


async def seed_demo_course() -> bool:
    async with SessionLocal() as session:
        exists = await session.scalar(select(Course).where(Course.title == DEMO_TITLE))
        if exists is not None:
            return False

        course = Course(
            title=DEMO_TITLE,
            description="Вводный курс по программированию на Python для детей 10–14 лет.",
            track=CourseTrack.PYTHON,
            age_min=10,
            age_max=14,
            level=CourseLevel.BEGINNER,
            is_published=True,
        )

        # Модуль 1
        m1 = Module(course=course, title="Знакомство с Python", order_index=1)
        Lesson(
            module=m1, title="Что такое программирование", order_index=1,
            theory_md="# Программирование\nЭто способ объяснить компьютеру, что делать.",
        )
        l2 = Lesson(
            module=m1, title="Первая программа: print", order_index=2,
            theory_md="Функция `print()` выводит текст на экран.",
        )
        quiz = Assignment(lesson=l2, type=AssignmentType.QUIZ, title="Проверь себя", max_score=100)
        quiz.questions.append(Question(
            text="Какая функция выводит текст на экран в Python?",
            kind=QuestionKind.SINGLE,
            options_json=["print()", "echo", "console.log()"],
            correct_json=[0],
        ))

        # Модуль 2
        m2 = Module(course=course, title="Переменные и числа", order_index=2)
        l3 = Lesson(
            module=m2, title="Переменные", order_index=1,
            theory_md="Переменная хранит значение: `x = 5`.",
        )
        code = Assignment(lesson=l3, type=AssignmentType.CODE, title="Квадрат числа", max_score=100)
        code.code_tests.append(CodeTest(stdin="5\n", expected_stdout="25", is_hidden=False, weight=1))
        code.code_tests.append(CodeTest(stdin="9\n", expected_stdout="81", is_hidden=True, weight=1))
        Lesson(
            module=m2, title="Арифметика", order_index=2,
            theory_md="Python умеет складывать, вычитать, умножать и делить числа.",
        )

        session.add(course)
        await session.commit()
        return True


async def main() -> None:
    created = await seed_demo_course()
    print(f"seed demo content: {'создан' if created else 'уже существует'} ({DEMO_TITLE})")


if __name__ == "__main__":
    asyncio.run(main())
