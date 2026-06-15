"""Smoke-тесты Этапа 0: приложение собирается, маршрут health зарегистрирован.

Эти тесты не требуют поднятых PostgreSQL/Redis — они проверяют только сборку
приложения и наличие маршрутов.
"""
from app.main import create_app


def test_app_builds():
    app = create_app()
    assert app.title


def test_health_route_registered():
    app = create_app()
    paths = {route.path for route in app.routes}
    assert "/api/v1/health" in paths
