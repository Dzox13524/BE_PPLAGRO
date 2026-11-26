"""RBAC dependencies: get_current_user, require_owner, require_karyawan."""
from typing import Any

import jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.exceptions import AppException
from app.core import token_blacklist
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.employees.models import User

# tokenUrl -> endpoint form OAuth2 agar tombol "Authorize" di Swagger UI bisa login langsung
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token",
    auto_error=False,
    scheme_name="JWT Bearer",
    description="Isi username (`owner` atau `karyawan`) & password, atau gunakan token dari /auth/login.",
)

_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


def _unauthorized(message: str) -> AppException:
    return AppException(message, status.HTTP_401_UNAUTHORIZED, headers=_AUTH_HEADERS)


def get_token_payload(
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """Validasi JWT (signature, expiry, blacklist) dan kembalikan payload-nya."""
    if not token:
        raise _unauthorized("Tidak terautentikasi. Sertakan header 'Authorization: Bearer <token>'.")
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise _unauthorized("Token telah kedaluwarsa, silakan login kembali.")
    except jwt.PyJWTError:
        raise _unauthorized("Token tidak valid.")

    jti = payload.get("jti")
    if not jti:
        raise _unauthorized("Token tidak valid.")
    if token_blacklist.contains(jti):
        raise _unauthorized("Token sudah tidak berlaku (telah logout).")
    return payload


def get_current_user(
    payload: dict[str, Any] = Depends(get_token_payload),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise _unauthorized("Token tidak valid.")

    user = db.get(User, user_id)
    if user is None:
        raise _unauthorized("Pengguna tidak ditemukan.")
    return user


def require_roles(*roles: UserRole):
    """Factory dependency untuk membatasi endpoint berdasarkan role."""
    allowed = set(roles)
    allowed_label = ", ".join(r.value for r in roles)

    def _role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise AppException(
                f"Akses ditolak. Endpoint ini hanya untuk role: {allowed_label}.",
                status.HTTP_403_FORBIDDEN,
            )
        return user

    return _role_checker


# owner saja: Manajemen Karyawan & Manajemen Stok
require_owner = require_roles(UserRole.owner)

# karyawan (dan owner sebagai supervisor): Tanaman, Prediksi Pertumbuhan, Diagnosis
require_karyawan = require_roles(UserRole.karyawan, UserRole.owner)
