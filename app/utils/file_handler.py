"""Validasi & penyimpanan file gambar upload + pembuatan URL publik."""
import io
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.common.exceptions import AppException
from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/pjpeg", "application/octet-stream"}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "MPO"}  # MPO = JPEG dari beberapa kamera HP


@dataclass
class SavedImage:
    relative_path: str      # contoh: diagnosis/2026/11/abc123.jpg (relatif terhadap uploads/)
    absolute_path: Path
    original_filename: str | None
    content_type: str | None
    size_bytes: int
    content: bytes

    @property
    def public_url(self) -> str:
        return build_public_url(self.relative_path)


def build_public_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    return f"{settings.PUBLIC_BASE_URL.rstrip('/')}/uploads/{relative_path.lstrip('/')}"


async def save_upload_image(file: UploadFile, subdir: str = "diagnosis") -> SavedImage:
    """Validasi ekstensi, content-type, ukuran & isi gambar (.jpg/.png), lalu simpan ke uploads/<subdir>/YYYY/MM/."""
    if file is None or not file.filename:
        raise AppException("File gambar wajib diunggah.", status.HTTP_400_BAD_REQUEST)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AppException(
            f"Format file '{ext or '-'}' tidak didukung. Gunakan .jpg, .jpeg, atau .png.",
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )
    if file.content_type and file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise AppException(f"Content-Type '{file.content_type}' tidak didukung.", status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    content = await file.read(settings.max_upload_bytes + 1)
    await file.close()
    if not content:
        raise AppException("File kosong.", status.HTTP_400_BAD_REQUEST)
    if len(content) > settings.max_upload_bytes:
        raise AppException(f"Ukuran file melebihi batas {settings.MAX_UPLOAD_SIZE_MB} MB.",
                           status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    try:
        with Image.open(io.BytesIO(content)) as img:
            img_format = (img.format or "").upper()
            img.verify()
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise AppException("File bukan gambar yang valid atau rusak.", status.HTTP_400_BAD_REQUEST)
    if img_format not in ALLOWED_PIL_FORMATS:
        raise AppException(f"Isi file berformat {img_format}, hanya JPEG/PNG yang didukung.",
                           status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    now = datetime.now()
    rel_dir = Path(subdir) / f"{now:%Y}" / f"{now:%m}"
    abs_dir = settings.UPLOAD_DIR / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    final_ext = ".png" if img_format == "PNG" else ".jpg"
    filename = f"{now:%Y%m%d%H%M%S}_{uuid.uuid4().hex[:12]}{final_ext}"
    abs_path = abs_dir / filename
    abs_path.write_bytes(content)

    return SavedImage(
        relative_path=(rel_dir / filename).as_posix(),
        absolute_path=abs_path,
        original_filename=file.filename,
        content_type=file.content_type,
        size_bytes=len(content),
        content=content,
    )


def delete_file(relative_path: str | None) -> None:
    if not relative_path:
        return
    try:
        path = (settings.UPLOAD_DIR / relative_path).resolve()
        if settings.UPLOAD_DIR.resolve() in path.parents and path.exists():
            path.unlink()
    except OSError:  # pragma: no cover
        logger.warning("Gagal menghapus file %s", relative_path)

