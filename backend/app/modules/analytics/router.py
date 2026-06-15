"""HTTP-эндпоинты аналитики и отчётов (дашборды по ролям)."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.db.enums import UserRole
from app.modules.analytics import service
from app.modules.analytics.schemas import (
    AdminOverview,
    ChildReport,
    GroupAnalytics,
    ParentOverview,
    ReportExportOut,
    StudentDashboard,
)
from app.modules.auth.deps import require_roles
from app.modules.users.models import User

router = APIRouter(prefix="/analytics", tags=["analytics"])
DbDep = Annotated[AsyncSession, Depends(get_db)]
StudentDep = Annotated[User, Depends(require_roles(UserRole.STUDENT))]
ParentDep = Annotated[User, Depends(require_roles(UserRole.PARENT))]
TeacherDep = Annotated[User, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))]
AdminDep = Annotated[User, Depends(require_roles(UserRole.ADMIN))]


@router.get("/me", response_model=StudentDashboard)
async def my_dashboard(student: StudentDep, db: DbDep):
    return await service.student_dashboard(db, student)


@router.get("/children", response_model=ParentOverview)
async def parent_overview(parent: ParentDep, db: DbDep):
    return await service.parent_overview(db, parent)


@router.get("/children/{child_id}", response_model=ChildReport)
async def child_report(child_id: int, parent: ParentDep, db: DbDep):
    return await service.child_report(db, parent, child_id)


@router.post("/children/{child_id}/report/export", response_model=ReportExportOut)
async def export_report(child_id: int, parent: ParentDep, db: DbDep):
    return await service.export_report(db, parent, child_id)


@router.get("/groups/{group_id}", response_model=GroupAnalytics)
async def group_analytics(group_id: int, teacher: TeacherDep, db: DbDep):
    return await service.group_analytics(db, teacher, group_id)


@router.get("/admin/overview", response_model=AdminOverview)
async def admin_overview(_admin: AdminDep, db: DbDep):
    return await service.admin_overview(db)
