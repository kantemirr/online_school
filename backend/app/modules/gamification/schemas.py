"""Pydantic-схемы геймификации."""
from datetime import datetime

from pydantic import BaseModel


class MySummaryOut(BaseModel):
    xp: int
    streak: int
    rank_global: int | None
    achievements_earned: int
    achievements_total: int


class AchievementOut(BaseModel):
    code: str
    title: str
    description: str | None
    icon: str | None
    earned: bool
    earned_at: datetime | None = None


class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    nickname: str | None
    score: float


class LeaderboardOut(BaseModel):
    entries: list[LeaderboardEntry]
    my_rank: int | None
    my_score: float | None
