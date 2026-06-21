"""Сид демонстрационного контента каталога (8 курсов).

Запуск: `python -m app.db.seeds_content`
Идемпотентно: курс с известным названием не пересоздаётся.

Демо-курс «Python с нуля для детей» создаётся ПЕРВЫМ и не меняется — на его
квиз (верный вариант индекс 0) и код-задание «Квадрат числа» завязаны тесты.
Остальные 7 курсов задаются декларативно (CATALOG) и строятся builder'ом.
"""
import asyncio
from decimal import Decimal

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

INTRO_THEORY_MD = """# Что такое программирование

Представь, что у тебя есть очень исполнительный, но совсем не догадливый помощник —
**компьютер**. Он умеет считать с невероятной скоростью, рисовать, играть музыку и
запускать игры. Но есть одна хитрость: сам по себе он не знает, что делать. Ему нужно
**объяснить каждый шаг**. Вот это объяснение и называется *программированием*.

> **Программирование** — это способ дать компьютеру понятные пошаговые инструкции,
> чтобы он выполнил то, что мы задумали.

## Компьютер выполняет инструкции

Компьютер похож на робота из сказки: он делает **ровно то, что ему сказали** — не больше
и не меньше. Если в инструкции ошибка, он честно выполнит ошибку. Поэтому программист
должен думать чётко и по порядку.

Сравни две инструкции «приготовить бутерброд»:

- 🙂 *Возьми хлеб. Намажь масло. Положи сыр.* — понятно и по шагам.
- 🤔 *Сделай бутерброд.* — а как именно? Робот растеряется.

Компьютеру нужен **первый** вариант — подробный и пошаговый.

## Алгоритм — это рецепт для компьютера

Последовательность шагов, которая решает задачу, называется **алгоритмом**. Это как
рецепт в кулинарной книге или инструкция к конструктору.

Алгоритм «перейти дорогу»:

1. Подойти к переходу.
2. Посмотреть налево и направо.
3. Дождаться зелёного света.
4. Убедиться, что машины остановились.
5. Перейти дорогу.

Любая программа — это алгоритм, записанный на языке, который понимает компьютер.

## Где живёт программирование

Программы окружают нас повсюду. Их написали программисты:

- 🎮 **Игры** — от мобильных до больших компьютерных миров.
- 🌐 **Сайты и приложения** — YouTube, карты, мессенджеры.
- 🤖 **Роботы и умные устройства** — пылесосы, колонки, машины.
- 🚀 **Наука и космос** — расчёты для ракет и телескопов.

Всё это — результат того, что кто-то однажды объяснил компьютеру, что делать.

## На чём «разговаривают» с компьютером

Чтобы давать инструкции, придумали **языки программирования**. Их много, и у каждого
свой характер:

- **Scratch** — язык из ярких блоков-пазлов, с него удобно начинать.
- **Python** — наш язык в этом курсе. Команды на нём короткие и читаются почти как
  обычный английский, поэтому он отлично подходит для первых шагов.

## Самая первая команда

В Python вывести надпись на экран можно одной строчкой:

```python
print("Привет, мир!")
```

Команда `print` означает «напечатай», а в кавычках мы пишем то, что хотим показать.
Запусти такую программу — и компьютер послушно выведет: `Привет, мир!`

## Что развивает программирование

Когда ты пишешь код, ты тренируешь полезные суперспособности:

- **Логику** — выстраивать шаги по порядку.
- **Внимание** — замечать мелочи (компьютер не прощает опечаток).
- **Творчество** — придумывать свои игры и проекты.
- **Терпение** — искать и исправлять ошибки. Это нормально, ошибаются все!

## Что дальше

На следующих уроках ты познакомишься с командой `print`, научишься хранить данные в
**переменных** и решишь первую настоящую задачу с автоматической проверкой. Поехали! 🚀
"""


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

        m1 = Module(course=course, title="Знакомство с Python", order_index=1)
        Lesson(
            module=m1, title="Что такое программирование", order_index=1,
            video_url="https://www.youtube.com/embed/nKIu9yen5nc",
            theory_md=INTRO_THEORY_MD,
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


# ── Декларативный каталог (ещё 7 курсов) ─────────────────────────────────────
def _q(text, options, correct, kind=QuestionKind.SINGLE):
    return {"text": text, "kind": kind, "options": options, "correct": correct}


def _t(stdin, expected, hidden=False):
    return {"stdin": stdin, "expected": expected, "hidden": hidden}


CATALOG: list[dict] = [
    {
        "title": "Scratch: первые игры",
        "description": "Визуальное программирование: собираем первую игру из блоков.",
        "track": CourseTrack.SCRATCH, "level": CourseLevel.BEGINNER,
        "age_min": 8, "age_max": 10, "price": Decimal("0.00"),
        "modules": [
            {"title": "Знакомство со Scratch", "lessons": [
                {"title": "Сцена и спрайты", "theory_md": "**Спрайт** — это персонаж. **Сцена** — фон, где он живёт.",
                 "assignments": [{"type": "quiz", "title": "Основы Scratch", "questions": [
                     _q("Как называется персонаж в Scratch?", ["Спрайт", "Робот", "Пиксель"], [0]),
                     _q("Из чего собирают программу в Scratch?", ["Из блоков", "Из текста", "Из чисел"], [0]),
                     _q("Что такое сцена?", ["Фон, где живёт спрайт", "Кнопка запуска", "Звук"], [0]),
                     _q("Какие элементы можно добавить на сцену?", ["Спрайты", "Фоны", "Числа подряд"], [0, 1],
                        kind=QuestionKind.MULTIPLE),
                 ]}]},
                {"title": "Движение и события", "theory_md": "Блок «когда нажат флажок» запускает программу. Блоки движения двигают спрайт.",
                 "assignments": [{"type": "quiz", "title": "Движение", "questions": [
                     _q("Какой блок запускает программу?", ["Когда нажат флажок", "Идти 10 шагов", "Повернуть"], [0]),
                     _q("Что делает блок «идти 10 шагов»?", ["Двигает спрайт вперёд", "Меняет фон", "Издаёт звук"], [0]),
                     _q("Чем отличается событие от движения?", ["Событие запускает, движение перемещает", "Ничем", "Событие — это звук"], [0]),
                 ]}]},
            ]},
            {"title": "Делаем игру", "lessons": [
                {"title": "Цикл и условие", "theory_md": "Цикл повторяет действия. Условие проверяет, например, касание края.",
                 "assignments": []},
                {"title": "Проект: своя игра", "theory_md": "Собери простую игру: герой ловит падающие предметы.",
                 "assignments": [{"type": "project", "title": "Моя первая игра"}]},
            ]},
        ],
    },
    {
        "title": "Scratch: анимация и истории",
        "description": "Создаём мультфильмы и интерактивные истории в Scratch.",
        "track": CourseTrack.SCRATCH, "level": CourseLevel.BEGINNER,
        "age_min": 9, "age_max": 11, "price": Decimal("0.00"),
        "modules": [
            {"title": "Костюмы и анимация", "lessons": [
                {"title": "Смена костюмов", "theory_md": "Анимация — это быстрая смена костюмов спрайта.",
                 "assignments": [{"type": "quiz", "title": "Анимация", "questions": [
                     _q("Что создаёт анимацию персонажа?", ["Смена костюмов", "Смена фона", "Звук"], [0]),
                     _q("Зачем нужен блок «ждать»?", ["Замедлить смену кадров", "Ускорить программу", "Удалить спрайт"], [0]),
                     _q("Что показывает блок «говорить»?", ["Реплику персонажа", "Фон", "Очки"], [0]),
                     _q("Что можно добавить в историю?", ["Диалоги", "Звук", "Случайные ошибки"], [0, 1],
                        kind=QuestionKind.MULTIPLE),
                 ]}]},
                {"title": "Диалоги и звук", "theory_md": "Блок «говорить» показывает реплику. Можно добавить звук.",
                 "assignments": [{"type": "project", "title": "Анимированная история"}]},
            ]},
        ],
    },
    {
        "title": "Python: продолжаем",
        "description": "Условия, циклы и строки на Python с практикой в песочнице.",
        "track": CourseTrack.PYTHON, "level": CourseLevel.INTERMEDIATE,
        "age_min": 11, "age_max": 14, "price": Decimal("1290.00"),
        "modules": [
            {"title": "Условия", "lessons": [
                {"title": "if / else", "theory_md": "`if` выполняет код при условии, `else` — иначе.",
                 "assignments": [
                     {"type": "quiz", "title": "Условия", "questions": [
                         _q("Что выполнит `if x > 0:`?", ["Код, если x больше 0", "Код всегда", "Ничего"], [0]),
                         _q("Когда выполнится ветка `else`?", ["Если условие ложно", "Если условие истинно", "Всегда"], [0]),
                         _q("Какой оператор проверяет равенство?", ["==", "=", "=>"], [0]),
                         _q("Какие значения логического типа есть в Python?", ["True", "False", "Maybe"], [0, 1],
                            kind=QuestionKind.MULTIPLE),
                     ]},
                     {"type": "code", "title": "Чётное или нечётное",
                      "tests": [_t("4\n", "чётное"), _t("7\n", "нечётное", hidden=True)]},
                 ]},
            ]},
            {"title": "Циклы", "lessons": [
                {"title": "Цикл for", "theory_md": "`for i in range(n)` повторяет действие n раз.",
                 "assignments": [
                     {"type": "code", "title": "Сумма от 1 до N",
                      "tests": [_t("5\n", "15"), _t("10\n", "55", hidden=True)]},
                 ]},
                {"title": "FizzBuzz", "theory_md": "Классическая задача: делимость на 3 и 5.",
                 "assignments": [
                     {"type": "code", "title": "FizzBuzz",
                      "tests": [_t("15\n", "FizzBuzz"), _t("3\n", "Fizz"), _t("5\n", "Buzz", hidden=True), _t("7\n", "7", hidden=True)]},
                 ]},
            ]},
            {"title": "Строки", "lessons": [
                {"title": "Работа со строками", "theory_md": "Строки можно переворачивать срезом `s[::-1]`.",
                 "assignments": [
                     {"type": "code", "title": "Переверни строку",
                      "tests": [_t("привет\n", "тевирп"), _t("код\n", "док", hidden=True)]},
                 ]},
            ]},
        ],
    },
    {
        "title": "Python: игры с черепашкой",
        "description": "Рисуем и программируем с модулем turtle — весело и наглядно.",
        "track": CourseTrack.PYTHON, "level": CourseLevel.BEGINNER,
        "age_min": 10, "age_max": 13, "price": Decimal("990.00"),
        "modules": [
            {"title": "Черепашья графика", "lessons": [
                {"title": "Первые шаги черепашки", "theory_md": "`forward()` двигает черепашку, `right()` поворачивает.",
                 "assignments": [{"type": "quiz", "title": "Turtle", "questions": [
                     _q("Что делает `forward(100)`?", ["Двигает вперёд на 100", "Рисует круг", "Меняет цвет"], [0]),
                     _q("Что делает `right(90)`?", ["Поворачивает направо на 90°", "Двигает вправо", "Рисует квадрат"], [0]),
                     _q("Зачем нужен `penup()`?", ["Поднять перо, чтобы не рисовать", "Опустить перо", "Стереть рисунок"], [0]),
                     _q("Как нарисовать квадрат?", ["4 раза «вперёд + поворот 90°»", "1 раз вперёд", "Поворот на 360°"], [0]),
                 ]}]},
                {"title": "Рисуем квадрат", "theory_md": "Квадрат — это 4 раза «вперёд + поворот на 90°».",
                 "assignments": [
                     {"type": "code", "title": "Периметр квадрата",
                      "tests": [_t("4\n", "16"), _t("7\n", "28", hidden=True)]},
                     {"type": "project", "title": "Рисунок черепашкой"},
                 ]},
            ]},
        ],
    },
    {
        "title": "Веб: HTML и CSS",
        "description": "Делаем первую веб-страницу: разметка HTML и стили CSS.",
        "track": CourseTrack.WEB, "level": CourseLevel.BEGINNER,
        "age_min": 11, "age_max": 14, "price": Decimal("0.00"),
        "modules": [
            {"title": "HTML", "lessons": [
                {"title": "Теги и структура", "theory_md": "HTML строится из **тегов**: `<h1>`, `<p>`, `<a>`.",
                 "assignments": [{"type": "quiz", "title": "HTML", "questions": [
                     _q("Какой тег для заголовка?", ["<h1>", "<p>", "<div>"], [0]),
                     _q("Какой тег для ссылки?", ["<a>", "<link>", "<href>"], [0]),
                     _q("Какой тег для абзаца текста?", ["<p>", "<text>", "<par>"], [0]),
                     _q("Что из этого — HTML-теги?", ["<h1>", "<p>", "<color>"], [0, 1],
                        kind=QuestionKind.MULTIPLE),
                 ]}]},
            ]},
            {"title": "CSS", "lessons": [
                {"title": "Стили и цвета", "theory_md": "CSS задаёт оформление: `color`, `font-size`, `background`.",
                 "assignments": [
                     {"type": "quiz", "title": "CSS", "questions": [
                         _q("Какое свойство задаёт цвет текста?", ["color", "background", "border"], [0]),
                         _q("Какое свойство задаёт размер шрифта?", ["font-size", "text-size", "size"], [0]),
                         _q("Какое свойство задаёт фон?", ["background", "color", "border"], [0]),
                         _q("Что из этого — свойства CSS?", ["color", "font-size", "tag-name"], [0, 1],
                            kind=QuestionKind.MULTIPLE),
                     ]},
                     {"type": "project", "title": "Моя страница о себе"},
                 ]},
            ]},
        ],
    },
    {
        "title": "Веб: интерактив на JavaScript",
        "description": "Оживляем страницу: переменные, события и DOM на JavaScript.",
        "track": CourseTrack.WEB, "level": CourseLevel.INTERMEDIATE,
        "age_min": 12, "age_max": 14, "price": Decimal("1490.00"),
        "modules": [
            {"title": "Основы JS", "lessons": [
                {"title": "Переменные и функции", "theory_md": "`let x = 5;` — переменная. `function f(){}` — функция.",
                 "assignments": [{"type": "quiz", "title": "JavaScript", "questions": [
                     _q("Как объявить переменную в JS?", ["let x = 5", "x := 5", "var: x"], [0]),
                     _q("Как объявить функцию?", ["function f(){}", "func f[]", "def f():"], [0]),
                     _q("Что делает `addEventListener('click', ...)`?", ["Реагирует на клик", "Создаёт переменную", "Удаляет элемент"], [0]),
                     _q("Какие ключевые слова объявляют переменную в JS?", ["let", "const", "make"], [0, 1],
                        kind=QuestionKind.MULTIPLE),
                 ]}]},
                {"title": "События и DOM", "theory_md": "`addEventListener('click', ...)` реагирует на клик.",
                 "assignments": [{"type": "project", "title": "Интерактивная кнопка"}]},
            ]},
        ],
    },
    {
        "title": "Алгоритмы на Python",
        "description": "Базовые алгоритмы и решение задач с автопроверкой в песочнице.",
        "track": CourseTrack.ALGORITHMS, "level": CourseLevel.INTERMEDIATE,
        "age_min": 12, "age_max": 14, "price": Decimal("1290.00"),
        "modules": [
            {"title": "Числа", "lessons": [
                {"title": "Максимум и минимум", "theory_md": "Сравнение чисел: `max(a, b)`.",
                 "assignments": [
                     {"type": "code", "title": "Максимум из двух",
                      "tests": [_t("3 8\n", "8"), _t("10 2\n", "10", hidden=True)]},
                 ]},
                {"title": "Факториал", "theory_md": "Факториал n! = 1·2·…·n.",
                 "assignments": [
                     {"type": "code", "title": "Факториал",
                      "tests": [_t("5\n", "120"), _t("3\n", "6", hidden=True)]},
                 ]},
                {"title": "Простое число", "theory_md": "Простое число делится только на 1 и само себя.",
                 "assignments": [
                     {"type": "quiz", "title": "Простые числа", "questions": [
                         _q("Какое из чисел простое?", ["7", "8", "9"], [0]),
                         _q("На что делится простое число?", ["На 1 и само себя", "На любое число", "Только на 2"], [0]),
                         _q("Какие из чисел простые?", ["2", "3", "4"], [0, 1],
                            kind=QuestionKind.MULTIPLE),
                     ]},
                     {"type": "code", "title": "Простое ли число",
                      "tests": [_t("7\n", "да"), _t("8\n", "нет", hidden=True)]},
                 ]},
            ]},
            {"title": "Строки", "lessons": [
                {"title": "Подсчёт гласных", "theory_md": "Перебираем символы и считаем гласные.",
                 "assignments": [
                     {"type": "code", "title": "Сколько гласных",
                      "tests": [_t("привет\n", "2"), _t("программа\n", "3", hidden=True)]},
                 ]},
            ]},
        ],
    },
]

_TYPE = {"quiz": AssignmentType.QUIZ, "code": AssignmentType.CODE, "project": AssignmentType.PROJECT}


def _build_course(session, spec: dict) -> Course:
    course = Course(
        title=spec["title"], description=spec["description"], track=spec["track"],
        level=spec["level"], age_min=spec["age_min"], age_max=spec["age_max"],
        price=spec["price"], is_published=True,
    )
    for mi, mspec in enumerate(spec["modules"], start=1):
        module = Module(course=course, title=mspec["title"], order_index=mi)
        for li, lspec in enumerate(mspec["lessons"], start=1):
            lesson = Lesson(module=module, title=lspec["title"], order_index=li,
                            theory_md=lspec.get("theory_md"))
            for aspec in lspec.get("assignments", []):
                assignment = Assignment(
                    lesson=lesson, type=_TYPE[aspec["type"]],
                    title=aspec["title"], max_score=aspec.get("max_score", 100),
                )
                for qspec in aspec.get("questions", []):
                    assignment.questions.append(Question(
                        text=qspec["text"], kind=qspec["kind"],
                        options_json=qspec["options"], correct_json=qspec["correct"],
                    ))
                for tspec in aspec.get("tests", []):
                    assignment.code_tests.append(CodeTest(
                        stdin=tspec["stdin"], expected_stdout=tspec["expected"],
                        is_hidden=tspec["hidden"], weight=1,
                    ))
    return course


async def seed_extra_courses() -> int:
    created = 0
    async with SessionLocal() as session:
        for spec in CATALOG:
            exists = await session.scalar(select(Course).where(Course.title == spec["title"]))
            if exists is not None:
                continue
            session.add(_build_course(session, spec))
            created += 1
        await session.commit()
    return created


async def main() -> None:
    demo = await seed_demo_course()
    extra = await seed_extra_courses()
    print(f"seed content: demo={'создан' if demo else 'есть'}, доп. курсов создано: {extra}")


if __name__ == "__main__":
    asyncio.run(main())
