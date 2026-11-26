"""Application settings loaded from environment variables / `.env` file."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Root folder project: lettuce-backend-api/
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Root folder
    BASE_DIR: Path = BASE_DIR

    # ----- Aplikasi -----
    APP_NAME: str = "Lettuce Management API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    # ----- Database -----
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'hidroponik_selada.db').as_posix()}"
    SQL_ECHO: bool = False

    # ----- JWT -----
    JWT_SECRET_KEY: str = "dev-secret-key-CHANGE-ME-in-production-please-0123456789"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # ----- CORS -----
    CORS_ORIGINS: str = "http://localhost,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001,http://localhost:8080"

    # ----- Upload & Model -----
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    ML_MODELS_DIR: Path = BASE_DIR / "ml_models"
    MAX_UPLOAD_SIZE_MB: int = 5
    DIAGNOSIS_MODEL_FILE: str = "best_lettuce_yolo26_v2.pt"
    DIAGNOSIS_TEMPERATURE_FILE: str = "temperature.txt"

    # ----- Seeder (sesuai kolom ERD `users`: nama, username, password, role) -----
    SEED_OWNER_NAMA: str = "Pemilik Mitra"
    SEED_OWNER_USERNAME: str = "owner"
    SEED_OWNER_PASSWORD: str = "owner123"
    SEED_KARYAWAN_NAMA: str = "Staf Kebun"
    SEED_KARYAWAN_USERNAME: str = "karyawan"
    SEED_KARYAWAN_PASSWORD: str = "karyawan123"
    SEED_SAMPLE_DATA: bool = True

    @property
    def cors_origins_list(self) -> list[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
