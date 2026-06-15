"""Клиент изолированной песочницы (Docker SDK) — защищаемое ядро ВКР.

Воркер запускает ОТДЕЛЬНЫЙ контейнер на каждый тест с жёсткой изоляцией:
сеть отключена, лимиты CPU/RAM/PIDs, файловая система только для чтения +
tmpfs, сброс всех capabilities, no-new-privileges, непривилегированный
пользователь, жёсткий таймаут. Код и stdin передаются через переменные
окружения (base64), результат — JSON из stdout контейнера.
"""
import asyncio
import base64
import json

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

_docker_client = None


def _client():
    global _docker_client
    if _docker_client is None:
        import docker  # импорт здесь, чтобы API без docker.sock не падал на старте
        _docker_client = docker.from_env()
    return _docker_client


def _b64(text: str) -> str:
    return base64.b64encode((text or "").encode("utf-8")).decode("ascii")


def _run_sync(code: str, stdin: str, timeout: int) -> dict:
    client = _client()
    environment = {
        "CODE_B64": _b64(code),
        "STDIN_B64": _b64(stdin),
        "TIMEOUT_SEC": str(timeout),
    }
    container = None
    try:
        container = client.containers.run(
            settings.SANDBOX_IMAGE,
            environment=environment,
            network_disabled=True,                       # сеть отключена
            mem_limit=settings.SANDBOX_MEM_LIMIT,         # лимит памяти
            nano_cpus=int(settings.SANDBOX_CPU_LIMIT * 1_000_000_000),  # лимит CPU
            pids_limit=settings.SANDBOX_PIDS_LIMIT,       # лимит числа процессов
            read_only=True,                               # ro файловая система
            tmpfs={"/tmp": "size=16m"},                   # writable временный раздел
            cap_drop=["ALL"],                             # сброс capabilities
            security_opt=["no-new-privileges:true"],
            user="1000:1000",                             # непривилегированный
            detach=True,
        )
        container.wait(timeout=timeout + 5)
        raw = container.logs(stdout=True, stderr=False).decode("utf-8", "ignore").strip()
        last_line = raw.splitlines()[-1] if raw else "{}"
        return json.loads(last_line)
    except Exception as exc:  # noqa: BLE001 — деградация при сбое песочницы
        logger.warning("sandbox run failed: %s", exc)
        return {
            "stdout": "", "stderr": f"Песочница недоступна: {exc}",
            "exit_code": -1, "timed_out": False, "duration_ms": 0, "infra_error": True,
        }
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except Exception:  # noqa: BLE001
                pass


async def run_in_sandbox(code: str, stdin: str, timeout: int) -> dict:
    """Асинхронная обёртка: блокирующий вызов Docker — в отдельном потоке."""
    return await asyncio.to_thread(_run_sync, code, stdin, timeout)
