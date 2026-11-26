"""Authentication endpoints (owner & karyawan)."""
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.common.responses import COMMON_ERROR_RESPONSES, APIResponse, success_response
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_token_payload
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, OAuth2TokenResponse, TokenResponse
from app.modules.employees.models import User
from app.modules.employees.schemas import UserOut

router = APIRouter(prefix="/auth", tags=["A. Authentication"])


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="Login (JSON) - untuk Frontend Laravel",
    responses={401: COMMON_ERROR_RESPONSES[401], 403: COMMON_ERROR_RESPONSES[403]},
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login dengan `username` & `password`. Mengembalikan JWT Access Token dan role user."""
    user = service.authenticate(db, payload.identifier, payload.password)
    return success_response(service.issue_token(user), f"Login berhasil sebagai {user.role.value}")


@router.post(
    "/token",
    response_model=OAuth2TokenResponse,
    summary="Login (form OAuth2) - dipakai tombol Authorize di Swagger UI",
)
def login_oauth2_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict[str, Any]:
    """Endpoint khusus Swagger UI (format OAuth2 standar). Frontend Laravel gunakan `POST /auth/login`."""
    user = service.authenticate(db, form.username, form.password)
    token = service.issue_token(user)
    return {"access_token": token["access_token"], "token_type": "bearer"}


@router.post("/logout", response_model=APIResponse[None], summary="Logout (blacklist token)",
             responses=COMMON_ERROR_RESPONSES)
def logout(payload: dict = Depends(get_token_payload)):
    service.logout(payload)
    return success_response(None, "Logout berhasil. Token telah dinonaktifkan.")


@router.get("/me", response_model=APIResponse[UserOut], summary="Profil user yang sedang login",
            responses=COMMON_ERROR_RESPONSES)
def me(current_user: User = Depends(get_current_user)):
    return success_response(UserOut.model_validate(current_user), "Profil pengguna")
