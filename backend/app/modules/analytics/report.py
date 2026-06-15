"""Формирование HTML-отчёта об успеваемости (выходной документ ВКР).

HTML без сторонних зависимостей; печатается в PDF из браузера. Сохраняется в
UPLOADS_DIR/reports/ фоновой задачей generate_report.
"""
import html as html_lib
import os
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.analytics import repository as repo
from app.modules.users.models import StudentProfile

settings = get_settings()


def _render(nickname: str, courses: list[dict], att: dict, achievements: list[dict]) -> str:
    esc = html_lib.escape
    rows = "".join(
        f"<tr><td>{esc(c['title'])}</td><td>{c['progress_pct']}%</td>"
        f"<td>{esc(c['status'])}</td><td>{c['completed_lessons']}</td><td>{c['avg_score']}</td></tr>"
        for c in courses
    ) or '<tr><td colspan="5">Нет записей на курсы</td></tr>'
    achs = ", ".join(esc(a["title"]) for a in achievements) or "пока нет"
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<title>Отчёт об успеваемости — {esc(nickname)}</title>
<style>body{{font-family:'Segoe UI',sans-serif;margin:40px;color:#1f2330}}
h1{{color:#3a48c8}}table{{border-collapse:collapse;width:100%;margin-top:12px}}
th,td{{border:1px solid #ccc;padding:8px;text-align:left}}th{{background:#f0f1fb}}
.muted{{color:#666}}</style></head><body>
<h1>Отчёт об успеваемости</h1>
<p>Ученик: <b>{esc(nickname)}</b><br><span class="muted">Сформировано: {datetime.now():%d.%m.%Y %H:%M}</span></p>
<h2>Прогресс по курсам</h2>
<table><tr><th>Курс</th><th>Прогресс</th><th>Статус</th><th>Завершено уроков</th><th>Средний балл</th></tr>{rows}</table>
<h2>Посещаемость</h2>
<p>Присутствий: {att['present']} · Пропусков: {att['absent']} · Уважительных: {att['excused']} · Доля присутствий: <b>{att['rate']}%</b></p>
<h2>Достижения</h2><p>{achs}</p>
</body></html>"""


async def build_report_html(db: AsyncSession, child_id: int) -> str | None:
    """Строит HTML-отчёт об успеваемости (для скачивания и для фоновой задачи)."""
    child = await db.get(StudentProfile, child_id)
    if child is None:
        return None
    return _render(
        child.nickname,
        await repo.course_progress(db, child_id),
        await repo.attendance_summary(db, child_id),
        await repo.achievements_detail(db, child_id),
    )


async def generate_report_file(db: AsyncSession, child_id: int) -> str:
    html = await build_report_html(db, child_id)
    if html is None:
        return ""
    folder = os.path.join(settings.UPLOADS_DIR, "reports")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"report_{child_id}_{datetime.now():%Y%m%d_%H%M%S}.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path
