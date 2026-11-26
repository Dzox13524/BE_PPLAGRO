"""Custom exceptions & global exception handlers (semua error dikembalikan dalam format standar)."""
import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Exception domain aplikasi -> otomatis diubah menjadi response error standar."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors
        self.headers = headers


class NotFoundException(AppException):
    def __init__(self, message: str = "Data tidak ditemukan") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictException(AppException):
    def __init__(self, message: str = "Data sudah ada") -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Akses ditolak") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


def _error_body(message: str, errors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"status": "error", "message": message, "data": None}
    if errors:
        body["errors"] = errors
    return body


_HTTP_MESSAGES = {
    400: "Permintaan tidak valid",
    401: "Tidak terautentikasi",
    403: "Akses ditolak",
    404: "Resource tidak ditemukan",
    405: "Method tidak diizinkan",
    409: "Konflik data",
    413: "Ukuran file terlalu besar",
    415: "Tipe media tidak didukung",
    422: "Validasi gagal",
    500: "Terjadi kesalahan pada server",
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(_error_body(exc.message, exc.errors)),
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        if isinstance(exc.detail, str) and exc.detail:
            message = exc.detail
        else:
            message = _HTTP_MESSAGES.get(exc.status_code, "Terjadi kesalahan")
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(_error_body(message)),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for err in exc.errors():
            loc = [str(part) for part in err.get("loc", ()) if part not in ("body", "query", "path", "form")]
            errors.append(
                {
                    "field": ".".join(loc) if loc else None,
                    "message": err.get("msg", "Input tidak valid"),
                    "type": err.get("type"),
                }
            )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(_error_body("Validasi input gagal", errors)),
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("IntegrityError: %s", exc.orig)
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_body("Data bentrok dengan data lain (duplikat atau relasi tidak valid)"),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(_HTTP_MESSAGES[500]),
        )

