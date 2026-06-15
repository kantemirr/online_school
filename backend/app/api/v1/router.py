"""Корневой роутер API v1.

По мере реализации участков сюда подключаются роутеры модулей:
auth, users, catalog, learning, grading, gamification, scheduling,
payments, notifications, analytics, admin.
"""
from fastapi import APIRouter

from app.api.v1.routes import health

api_router = APIRouter()
api_router.include_router(health.router)

# Этап 2+: api_router.include_router(auth.router, prefix="/auth")
