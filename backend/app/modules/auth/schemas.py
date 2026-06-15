"""Pydantic-схемы аутентификации и управления аккаунтами."""
from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.db.enums import AgeGroup, UserRole


# ── Регистрация / верификация ───────────────────────────────────────────────
class RegisterParentIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=32)
    consent_pdn: bool

    @field_validator("consent_pdn")
    @classmethod
    def _consent_required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Требуется согласие на обработку персональных данных (ФЗ-152)")
        return v


class VerifyEmailIn(BaseModel):
    token: str


# ── Вход ────────────────────────────────────────────────────────────────────
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ChildLoginIn(BaseModel):
    login_username: str = Field(min_length=3, max_length=64)
    pin: str = Field(pattern=r"^\d{4,6}$")


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


# ── Сброс пароля ─────────────────────────────────────────────────────────────
class PasswordResetRequestIn(BaseModel):
    email: EmailStr


class PasswordResetConfirmIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ── Ответы ───────────────────────────────────────────────────────────────────
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: int
    email: str | None
    role: UserRole
    is_active: bool
    display_name: str | None = None


# ── Дети (управляются родителем) ─────────────────────────────────────────────
class CreateChildIn(BaseModel):
    nickname: str = Field(min_length=1, max_length=64)
    birth_date: date
    login_username: str = Field(min_length=3, max_length=64)
    pin: str = Field(pattern=r"^\d{4,6}$")


class UpdateChildIn(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=64)
    pin: str | None = Field(default=None, pattern=r"^\d{4,6}$")


class ChildOut(BaseModel):
    user_id: int
    nickname: str
    birth_date: date
    age_group: AgeGroup
    login_username: str | None
    xp: int
    streak: int


# ── Создание пользователей администратором ───────────────────────────────────
class CreateStaffIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
    full_name: str = Field(min_length=1, max_length=255)
    specialization: str | None = Field(default=None, max_length=255)

    @field_validator("role")
    @classmethod
    def _staff_only(cls, v: UserRole) -> UserRole:
        if v not in (UserRole.TEACHER, UserRole.ADMIN):
            raise ValueError("Через эту операцию создаются только teacher или admin")
        return v
