"""Schemas untuk tabel `users` & manajemen karyawan (sesuai ERD)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.common.enums import UserRole

_USERNAME_PATTERN = r"^[a-zA-Z0-9_.@-]+$"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nama: str
    username: str
    role: UserRole
    created_at: datetime | None = None
    updated_at: datetime | None = None


class EmployeeCreate(BaseModel):
    """Menerima `nama` (ERD) atau alias `name`; `username` wajib."""

    nama: str | None = Field(None, min_length=2, max_length=100, examples=["Budi Santoso"])
    name: str | None = Field(None, min_length=2, max_length=100, description="Alias untuk `nama`")
    username: str = Field(..., min_length=3, max_length=50, pattern=_USERNAME_PATTERN, examples=["budi"])
    password: str = Field(..., min_length=6, max_length=72, examples=["rahasia123"])
    role: UserRole = Field(default=UserRole.karyawan)

    @model_validator(mode="after")
    def _ensure_nama(self) -> "EmployeeCreate":
        if not self.nama and self.name:
            self.nama = self.name
        if not self.nama:
            self.nama = self.username
        return self


class EmployeeUpdate(BaseModel):
    nama: str | None = Field(None, min_length=2, max_length=100)
    name: str | None = Field(None, min_length=2, max_length=100, description="Alias untuk `nama`")
    username: str | None = Field(None, min_length=3, max_length=50, pattern=_USERNAME_PATTERN)
    role: UserRole | None = None
    password: str | None = Field(None, min_length=6, max_length=72, description="Isi untuk reset password")

    @model_validator(mode="after")
    def _sync_nama(self) -> "EmployeeUpdate":
        if self.nama is None and self.name is not None:
            self.nama = self.name
        return self
