"""Time helpers. Semua timestamp disimpan sebagai *naive UTC* agar konsisten di SQLite/PostgreSQL/MySQL."""
from datetime import date, datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def today() -> date:
    return date.today()

