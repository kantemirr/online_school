"""Криптография и JWT.

- Пароли и PIN хешируются argon2 (устойчив к перебору на GPU).
- Токены — JWT (HS256): короткоживущий access и долгоживущий refresh.
  Каждый токен несёт уникальный jti — он используется для отзыва refresh
  через Redis (см. app/modules/auth/tokens.py).
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings
from app.core.exceptions import AuthError

_settings = get_settings()
_hasher = PasswordHasher()

ACCESS = "access"
REFRESH = "refresh"


# ── Пароли / PIN ──────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return _hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _hasher.verify(hashed, plain)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


# PIN ребёнка хешируется тем же алгоритмом.
hash_pin = hash_password
verify_pin = verify_password


# ── JWT ───────────────────────────────────────────────────────────────────
def _encode(payload: dict, ttl: timedelta) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    jti = uuid4().hex
    body = {
        **payload,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    token = jwt.encode(body, _settings.JWT_SECRET, algorithm=_settings.JWT_ALGORITHM)
    return token, jti


def create_access_token(user_id: int, role: str) -> tuple[str, str]:
    return _encode(
        {"sub": str(user_id), "role": role, "type": ACCESS},
        timedelta(minutes=_settings.ACCESS_TOKEN_TTL_MIN),
    )


def create_refresh_token(user_id: int) -> tuple[str, str]:
    return _encode(
        {"sub": str(user_id), "type": REFRESH},
        timedelta(days=_settings.REFRESH_TOKEN_TTL_DAYS),
    )


def decode_token(token: str, expected_type: str) -> dict:
    """Декодирует и проверяет токен. Бросает AuthError при любой проблеме."""
    try:
        claims = jwt.decode(token, _settings.JWT_SECRET, algorithms=[_settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Срок действия токена истёк", code="token_expired") from exc
    except jwt.PyJWTError as exc:
        raise AuthError("Недействительный токен", code="token_invalid") from exc

    if claims.get("type") != expected_type:
        raise AuthError("Неверный тип токена", code="token_wrong_type")
    return claims
