"""Раннер песочницы — ЗАГЛУШКА Этапа 0.

Полная реализация — на Этапе 5b. Контракт (предварительный):
  • вход: JSON в stdin вида
      {"code": "<исходник ученика>", "stdin": "<входные данные теста>"}
  • выход: JSON в stdout вида
      {"stdout": "...", "stderr": "...", "exit_code": 0, "duration_ms": 12}

Жёсткая изоляция (сеть, лимиты CPU/RAM, ro-FS, cap-drop, seccomp, таймаут)
обеспечивается флагами `docker run` со стороны воркера, а не этим файлом.
"""
import json
import sys


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    # Этап 0: эхо-заглушка, реальное исполнение кода появится на Этапе 5b.
    result = {
        "stdout": "",
        "stderr": "runner stub: реализация на Этапе 5b",
        "exit_code": 0,
        "duration_ms": 0,
        "echo": {"has_code": bool(payload.get("code"))},
    }
    sys.stdout.write(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
