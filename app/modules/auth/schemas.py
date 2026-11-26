"""Schemas autentikasi."""
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.common.enums import UserRole
from app.modules.employees.schemas import UserOut


class LoginRequest(BaseModel):
    """Login menggunakan `username` (atau alias `email`) + `password`."""

    username: str | None = Field(None, description="Username pada tabel `users`", examples=["owner"])
    email: str | None = Field(None, description="Alias opsional (jika diisi `owner@mitra.com` otomatis diambil `owner`)",
                              examples=[None])
    password: str = Field(..., min_length=1, max_length=72, examples=["owner123"])

    @model_validator(mode="after")
    def _require_identifier(self) -> "LoginRequest":
        if not (self.username or self.email):
            raise ValueError("Field 'username' wajib diisi")
        return self

    @property
    def identifier(self) -> str:
        return (self.username or self.email or "").strip()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Masa berlaku token (detik)")
    expires_at: datetime = Field(..., description="Waktu kedaluwarsa (UTC)")
    role: UserRole
    user: UserOut


class OAuth2TokenResponse(BaseModel):
    """Format standar OAuth2 (dipakai tombol Authorize Swagger)."""

    access_token: str
    token_type: str = "bearer"
