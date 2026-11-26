"""Standardized JSON response wrapper: { status, message, data, meta }."""
import math
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Kontrak response standar untuk tim Frontend Laravel."""

    status: Literal["success", "error"] = "success"
    message: str = "Berhasil"
    data: T | None = None
    meta: dict[str, Any] | None = None


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    type: str | None = None


class APIErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    message: str
    data: Any = None
    errors: list[ErrorDetail] | None = Field(default=None)


def success_response(data: Any = None, message: str = "Berhasil", meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"status": "success", "message": message, "data": data, "meta": meta}


def pagination_meta(page: int, per_page: int, total: int, **extra: Any) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": math.ceil(total / per_page) if per_page else 0,
    }
    meta.update(extra)
    return meta


# Response docs untuk Swagger (dipakai di parameter `responses=` router)
COMMON_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    401: {"model": APIErrorResponse, "description": "Tidak terautentikasi / token tidak valid"},
    403: {"model": APIErrorResponse, "description": "Role tidak memiliki akses"},
    422: {"model": APIErrorResponse, "description": "Validasi input gagal"},
}

