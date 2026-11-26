"""SQLAlchemy 2.0 engine, session factory, declarative Base & DB initializer."""
from collections.abc import Generator
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum as SAEnum, create_engine, event, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

from app.common.time import utcnow
from app.core.config import settings

_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQL_ECHO,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

if settings.is_sqlite:
    # Aktifkan foreign key constraint (ON DELETE CASCADE / SET NULL / RESTRICT) di SQLite
    @event.listens_for(engine, "connect")
    def _sqlite_enable_fk(dbapi_connection, _connection_record):  # pragma: no cover
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base untuk seluruh model ORM."""


def db_enum(enum_cls: type[PyEnum], name: str) -> SAEnum:
    """ENUM native (MySQL) yang menyimpan *value* enum (lowercase) sesuai ERD."""
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e], validate_strings=True)


class CreatedAtMixin:
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime, default=utcnow, server_default=func.current_timestamp()
    )


class TimestampMixin(CreatedAtMixin):
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=utcnow)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: satu session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_all_models() -> None:
    """Import semua model agar terdaftar di Base.metadata sebelum create_all()."""
    from app.modules.diagnosis import models as _diagnosis  # noqa: F401
    from app.modules.employees import models as _employees  # noqa: F401
    from app.modules.knowledge_base import models as _kb  # noqa: F401
    from app.modules.plants import models as _plants  # noqa: F401
    from app.modules.stocks import models as _stocks  # noqa: F401


def init_db() -> None:
    """Buat seluruh tabel (auto-init). Untuk production disarankan memakai Alembic migration."""
    import_all_models()
    Base.metadata.create_all(bind=engine)
