"""Model `users` - sesuai ERD `hidroponik_selada`."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import UserRole
from app.core.database import Base, TimestampMixin, db_enum


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        db_enum(UserRole, "user_role"), default=UserRole.karyawan, server_default="karyawan", nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} username={self.username} role={self.role.value}>"
