"""Models `plants` & `growth_records` - sesuai ERD `hidroponik_selada`."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import PlantStatus
from app.core.database import Base, CreatedAtMixin, TimestampMixin, db_enum


class Plant(TimestampMixin, Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    kode_tanaman: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    nama: Mapped[str] = mapped_column(String(100), default="Selada", nullable=False)
    varietas: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tanggal_tanam: Mapped[date] = mapped_column(Date, nullable=False)
    tanggal_panen: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PlantStatus] = mapped_column(
        db_enum(PlantStatus, "plant_status"), default=PlantStatus.pembibitan, server_default="pembibitan", nullable=False
    )
    keterangan: Mapped[str | None] = mapped_column(Text, nullable=True)

    creator = relationship("User", foreign_keys=[created_by], lazy="joined")
    growth_records: Mapped[list["GrowthRecord"]] = relationship(
        back_populates="plant",
        cascade="all, delete-orphan",
        order_by=lambda: [GrowthRecord.tanggal_pengamatan, GrowthRecord.id],
    )
    diagnosis_records = relationship(
        "DiagnosisRecord",
        back_populates="plant",
        cascade="all, delete-orphan",
    )

    @property
    def created_by_nama(self) -> str | None:
        return self.creator.nama if self.creator else None

    @property
    def latest_growth_record(self) -> "GrowthRecord | None":
        return self.growth_records[-1] if self.growth_records else None

    @property
    def growth_record_count(self) -> int:
        return len(self.growth_records)


class GrowthRecord(CreatedAtMixin, Base):
    __tablename__ = "growth_records"
    __table_args__ = (
        Index("ix_growth_records_plant_tanggal", "plant_id", "tanggal_pengamatan"),
        Index("ix_growth_records_sumber_source_id", "sumber_data", "source_record_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False)
    recorded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tanggal_pengamatan: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    umur_tanaman: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Parameter morfologi
    tinggi_cm: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    jumlah_daun: Mapped[int | None] = mapped_column(Integer, nullable=True)
    berat_gram: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)

    # Parameter air dan lingkungan
    ph_air: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    suhu_air: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    ec: Mapped[Decimal | None] = mapped_column(Numeric(8, 3), nullable=True)
    suhu_c: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    kelembapan_persen: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    intensitas_cahaya: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Pelacakan dataset eksternal
    sumber_data: Mapped[str | None] = mapped_column(String(150), nullable=True)
    source_record_id: Mapped[str | None] = mapped_column(String(150), nullable=True)

    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)

    plant: Mapped["Plant"] = relationship(back_populates="growth_records")
    recorder = relationship("User", foreign_keys=[recorded_by], lazy="joined")

    @property
    def recorded_by_nama(self) -> str | None:
        return self.recorder.nama if self.recorder else None
