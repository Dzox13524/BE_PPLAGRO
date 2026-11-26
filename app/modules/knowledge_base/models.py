"""Models `disease_infos` & `nutrition_conditions` (Basis Pengetahuan) - sesuai ERD `hidroponik_selada`."""
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class DiseaseInfo(TimestampMixin, Base):
    __tablename__ = "disease_infos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama_penyakit: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    gejala: Mapped[str | None] = mapped_column(Text, nullable=True)
    penanganan_awal: Mapped[str | None] = mapped_column(Text, nullable=True)


class NutritionCondition(TimestampMixin, Base):
    __tablename__ = "nutrition_conditions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama_kondisi: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    unsur_nutrisi: Mapped[str | None] = mapped_column(String(100), nullable=True)
    deskripsi: Mapped[str | None] = mapped_column(Text, nullable=True)
    gejala: Mapped[str | None] = mapped_column(Text, nullable=True)
    penanganan_awal: Mapped[str | None] = mapped_column(Text, nullable=True)

