"""Password hashing (bcrypt) & JWT token utilities."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings

_BCRYPT_MAX_BYTES = 72  # batas bcrypt


def _to_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str | int, role: str, extra_claims: dict[str, Any] | None = None) -> dict[str, Any]:
    """Membuat JWT access token.

    Returns dict: {token, jti, expires_at (naive UTC), expires_in (detik)}
    """
    now = datetime.now(timezone.utc)
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + expires_delta
    jti = uuid.uuid4().hex
    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "jti": jti,
        "type": "access",
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return {
        "token": token,
        "jti": jti,
        "expires_at": expire.replace(tzinfo=None),
        "expires_in": int(expires_delta.total_seconds()),
    }


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode & verifikasi JWT. Raise `jwt.ExpiredSignatureError` / `jwt.PyJWTError` bila tidak valid."""
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    if payload.get("type") != "access":
        raise jwt.InvalidTokenError("Invalid token type")
    return payload

