"""Логика геймификации: начисления (хук), достижения, лидерборды."""
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.gamification import leaderboard, logic
from app.modules.gamification import repository as repo
from app.modules.gamification.models import StudentAchievement
from app.modules.gamification.schemas import (
    AchievementOut,
    LeaderboardEntry,
    LeaderboardOut,
    MySummaryOut,
)

XP_BASE = 10  # базовый XP за завершённый урок (сверх баллов задания)


# ── Хук завершения урока (синхронные начисления) ─────────────────────────────
async def award_for_lesson(
    db: AsyncSession, student_id: int, course_id: int,
    score: int | None, newly_completed: bool, progress_pct: float,
) -> None:
    profile = await repo.get_profile(db, student_id)
    if profile is None:
        return

    if newly_completed:
        profile.xp += XP_BASE + (score or 0)
        today = date.today()
        profile.streak = logic.compute_streak(profile.last_active_date, today, profile.streak)
        profile.last_active_date = today
        await db.commit()

    await evaluate_achievements(db, student_id)
    await leaderboard.update_global(student_id, profile.xp)
    await leaderboard.update_course(course_id, student_id, progress_pct)


async def recalc_leaderboards(db: AsyncSession) -> None:
    """Перестраивает лидерборды из БД (восстановление Redis / периодический пересчёт)."""
    await leaderboard.clear(leaderboard.GLOBAL_KEY)
    for student_id, xp in await repo.all_students_xp(db):
        await leaderboard.update_global(student_id, xp)
    for course_id, student_id, pct in await repo.all_enrollment_progress(db):
        await leaderboard.update_course(course_id, student_id, pct)


async def evaluate_achievements(db: AsyncSession, student_id: int) -> int:
    """Выдаёт недостающие достижения по текущей статистике. Возвращает число новых."""
    stats = await repo.compute_student_stats(db, student_id)
    earned = await repo.earned_ids(db, student_id)
    granted: list[tuple[str, str]] = []
    for achievement in await repo.list_achievements(db):
        if achievement.id not in earned and logic.is_earned(achievement.condition_json or {}, stats):
            db.add(StudentAchievement(student_id=student_id, achievement_id=achievement.id))
            granted.append((achievement.code, achievement.title))
    if granted:
        await db.commit()
        # Уведомление ученику (+ email родителю) по каждому новому достижению
        from app.modules.notifications import service as notifications
        for code, title in granted:
            await notifications.notify_achievement(db, student_id, code, title)
    return len(granted)


# ── Чтение для API ───────────────────────────────────────────────────────────
async def get_my_summary(db: AsyncSession, student_id: int) -> MySummaryOut:
    profile = await repo.get_profile(db, student_id)
    earned = await repo.earned_ids(db, student_id)
    total = len(await repo.list_achievements(db))
    return MySummaryOut(
        xp=profile.xp if profile else 0,
        streak=profile.streak if profile else 0,
        rank_global=await leaderboard.rank(leaderboard.GLOBAL_KEY, student_id),
        achievements_earned=len(earned),
        achievements_total=total,
    )


async def list_achievements(db: AsyncSession, student_id: int) -> list[AchievementOut]:
    earned = await repo.earned_map(db, student_id)
    return [
        AchievementOut(
            code=a.code, title=a.title, description=a.description, icon=a.icon,
            earned=a.id in earned, earned_at=earned.get(a.id),
        )
        for a in await repo.list_achievements(db)
    ]


async def get_leaderboard(db: AsyncSession, key: str, student_id: int, n: int = 10) -> LeaderboardOut:
    rows = await leaderboard.top(key, n)
    ids = [int(sid) for sid, _ in rows]
    names = await repo.nicknames(db, ids)
    entries = [
        LeaderboardEntry(
            rank=i + 1, student_id=int(sid), nickname=names.get(int(sid)), score=score,
        )
        for i, (sid, score) in enumerate(rows)
    ]
    return LeaderboardOut(
        entries=entries,
        my_rank=await leaderboard.rank(key, student_id),
        my_score=await leaderboard.score_of(key, student_id),
    )
