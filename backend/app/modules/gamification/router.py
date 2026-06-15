"""HTTP-эндпоинты геймификации."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.auth.deps import CurrentUser, require_roles
from app.modules.gamification import leaderboard, service
from app.modules.gamification.schemas import (
    AchievementOut,
    LeaderboardOut,
    MySummaryOut,
)
from app.modules.users.models import User

router = APIRouter(prefix="/gamification", tags=["gamification"])
DbDep = Annotated[AsyncSession, Depends(get_db)]
StudentDep = Annotated[User, Depends(require_roles(UserRole.STUDENT))]


@router.get("/me", response_model=MySummaryOut)
async def my_summary(student: StudentDep, db: DbDep):
    return await service.get_my_summary(db, student.id)


@router.get("/achievements", response_model=list[AchievementOut])
async def my_achievements(student: StudentDep, db: DbDep):
    return await service.list_achievements(db, student.id)


@router.get("/leaderboard", response_model=LeaderboardOut)
async def global_leaderboard(user: CurrentUser, db: DbDep, n: int = Query(default=10, ge=1, le=100)):
    return await service.get_leaderboard(db, leaderboard.GLOBAL_KEY, user.id, n)


@router.get("/leaderboard/courses/{course_id}", response_model=LeaderboardOut)
async def course_leaderboard(
    course_id: int, user: CurrentUser, db: DbDep, n: int = Query(default=10, ge=1, le=100)
):
    return await service.get_leaderboard(db, leaderboard.course_key(course_id), user.id, n)
