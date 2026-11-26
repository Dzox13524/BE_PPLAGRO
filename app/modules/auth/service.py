"""Business logic autentikasi: login, issue token, logout."""
from typing import Any

from fastapi import status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.exceptions import AppException
from app.core import token_blacklist
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.employees.models import User
from app.modules.employees.schemas import UserOut


def authenticate(db: Session, identifier: str, password: str) -> User:
    ident = identifier.strip().lower()
    # Jika klien mengirim format email (mis. `owner@mitra.com`), izinkan pencocokan dengan bagian sebelum `@`
    local_part = ident.split("@")[0]
    user = db.scalar(
        select(User).where(or_(func.lower(User.username) == ident, func.lower(User.username) == local_part))
    )
    if user is None:
        raise AppException("Username atau password salah.", status.HTTP_401_UNAUTHORIZED)

    stored_password = user.password or ""
    is_valid = verify_password(password, stored_password)
    if not is_valid and not stored_password.startswith("$2") and stored_password == password:
        user.password = hash_password(password)
        db.commit()
        db.refresh(user)
        is_valid = True

    if not is_valid:
        raise AppException("Username atau password salah.", status.HTTP_401_UNAUTHORIZED)
    return user


def issue_token(user: User) -> dict[str, Any]:
    token = create_access_token(
        subject=user.id, role=user.role.value, extra_claims={"username": user.username, "nama": user.nama}
    )
    return {
        "access_token": token["token"],
        "token_type": "bearer",
        "expires_in": token["expires_in"],
        "expires_at": token["expires_at"],
        "role": user.role,
        "user": UserOut.model_validate(user),
    }


def logout(payload: dict[str, Any]) -> None:
    token_blacklist.add(payload["jti"], float(payload["exp"]))
