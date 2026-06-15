"""Раннер песочницы (Этап 5b).

Исполняет код ученика в изолированном контейнере. Изоляция задаётся флагами
`docker run` со стороны воркера (сеть отключена, лимиты CPU/RAM/PIDs, ro-FS +
tmpfs, cap-drop ALL, no-new-privileges, непривилегированный пользователь).

Контракт:
  вход  — env CODE_B64 (base64 исходника), STDIN_B64 (base64 stdin теста),
          TIMEOUT_SEC (жёсткий таймаут на исполнение);
  выход — JSON в stdout: {stdout, stderr, exit_code, timed_out, duration_ms}.

Код ученика пишется в /tmp (tmpfs, writable) и запускается отдельным процессом
с подачей stdin и таймаутом; его вывод захватывается, а не печатается напрямую.
"""
import base64
import json
import os
import subprocess
import sys
import time


def _b64decode(value: str) -> str:
    return base64.b64decode(value or "").decode("utf-8", "ignore")


def main() -> None:
    code = _b64decode(os.environ.get("CODE_B64", ""))
    stdin_data = _b64decode(os.environ.get("STDIN_B64", ""))
    timeout = int(os.environ.get("TIMEOUT_SEC", "8"))

    solution_path = "/tmp/solution.py"
    with open(solution_path, "w", encoding="utf-8") as fh:
        fh.write(code)

    timed_out = False
    start = time.monotonic()
    try:
        proc = subprocess.run(
            [sys.executable, "-I", solution_path],
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout, stderr, exit_code = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + "\n[Превышено время выполнения]"
        exit_code = -1

    duration_ms = int((time.monotonic() - start) * 1000)
    sys.stdout.write(json.dumps({
        "stdout": stdout,
        "stderr": stderr,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
    }))


if __name__ == "__main__":
    main()
