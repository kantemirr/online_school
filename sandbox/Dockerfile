# Образ-исполнитель кода ученика (Этап 5b).
# Изоляция задаётся не здесь, а флагами `docker run` со стороны воркера:
#   --network none --memory 128m --cpus 0.5 --pids-limit 64
#   --read-only --tmpfs /tmp --cap-drop ALL --security-opt no-new-privileges
# Здесь же — только непривилегированный пользователь и минимальный runtime.
FROM python:3.12-slim

# Непривилегированный пользователь
RUN useradd --create-home --uid 1000 sandbox

USER sandbox
WORKDIR /home/sandbox

COPY --chown=sandbox:sandbox runner.py /home/sandbox/runner.py

# Точку входа задаёт воркер; по умолчанию — раннер.
ENTRYPOINT ["python", "/home/sandbox/runner.py"]
