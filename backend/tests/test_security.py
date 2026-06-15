"""Unit-тесты криптографии и JWT (без БД/Redis)."""
import time

import pytest

from app.core.exceptions import AuthError
from app.core.security import (
    ACCESS,
    REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    h = hash_password("s3cret!")
    assert h != "s3cret!"
    assert verify_password("s3cret!", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip():
    token, jti = create_access_token(user_id=42, role="parent")
    claims = decode_token(token, ACCESS)
    assert claims["sub"] == "42"
    assert claims["role"] == "parent"
    assert claims["type"] == ACCESS
    assert claims["jti"] == jti


def test_refresh_token_roundtrip():
    token, jti = create_refresh_token(user_id=7)
    claims = decode_token(token, REFRESH)
    assert claims["sub"] == "7"
    assert claims["jti"] == jti


def test_wrong_token_type_rejected():
    token, _ = create_access_token(user_id=1, role="admin")
    with pytest.raises(AuthError):
        decode_token(token, REFRESH)


def test_tampered_token_rejected():
    token, _ = create_access_token(user_id=1, role="admin")
    with pytest.raises(AuthError):
        decode_token(token + "x", ACCESS)
