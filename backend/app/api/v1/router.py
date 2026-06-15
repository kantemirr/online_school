"""Корневой роутер API v1.

По мере реализации участков сюда подключаются роутеры модулей:
auth, users, catalog, learning, grading, gamification, scheduling,
payments, notifications, analytics, admin.
"""
from fastapi import APIRouter

from app.api.v1.routes import health
from app.modules.auth.router import router as auth_router
from app.modules.catalog.admin_router import router as catalog_admin_router
from app.modules.catalog.router import router as catalog_router
from app.modules.gamification.router import router as gamification_router
from app.modules.grading.router import router as grading_router
from app.modules.learning.router import router as learning_router
from app.modules.notifications.router import router as notifications_router
from app.modules.payments.router import router as payments_router
from app.modules.scheduling.router import router as scheduling_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(catalog_router)
api_router.include_router(catalog_admin_router)
api_router.include_router(learning_router)
api_router.include_router(grading_router)
api_router.include_router(gamification_router)
api_router.include_router(scheduling_router)
api_router.include_router(notifications_router)
api_router.include_router(payments_router)
