"""Model `diagnosis_records` (Hasil Diagnosis Kesehatan Tanaman) - sesuai ERD `hidroponik_selada`."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import PlantPart
from app.core.database import Base, CreatedAtMixin, db_enum


class DiagnosisRecord(CreatedAtMixin, Base):
    __tablename__ = "diagnosis_records"
    __table_args__ = (
        Index("ix_diagnosis_records_plant_tanggal", "plant_id", "tanggal_diagnosis"),
        Index("ix_diagnosis_records_sumber_data", "sumber_data"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id", ondelete="CASCADE"), nullable=False)
    diagnosed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tanggal_diagnosis: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    plant_part: Mapped[PlantPart | None] = mapped_column(
        db_enum(PlantPart, "plant_part"), default=PlantPart.daun, server_default="daun", nullable=True
    )

    # Label keluaran model
    kelas_diagnosis: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(6, 5), nullable=True)

    # Referensi informasi diagnosis
    disease_info_id: Mapped[int | None] = mapped_column(
        ForeignKey("disease_infos.id", ondelete="SET NULL"), nullable=True
    )
    nutrition_condition_id: Mapped[int | None] = mapped_column(
        ForeignKey("nutrition_conditions.id", ondelete="SET NULL"), nullable=True
    )

    model: Mapped[str] = mapped_column(String(50), default="SVM", server_default="SVM", nullable=False)
    versi_model: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Pelacakan asal gambar atau dataset
    sumber_data: Mapped[str | None] = mapped_column(String(150), nullable=True)

    keterangan: Mapped[str | None] = mapped_column(Text, nullable=True)
    rekomendasi: Mapped[str | None] = mapped_column(Text, nullable=True)

    plant = relationship("Plant", back_populates="diagnosis_records", lazy="joined")
    diagnoser = relationship("User", foreign_keys=[diagnosed_by], lazy="joined")
    disease_info_rel = relationship("DiseaseInfo", lazy="joined")
    nutrition_condition_rel = relationship("NutritionCondition", lazy="joined")

    @property
    def diagnosed_by_nama(self) -> str | None:
        return self.diagnoser.nama if self.diagnoser else None

    @property
    def kode_tanaman(self) -> str | None:
        return self.plant.kode_tanaman if self.plant else None

    @property
    def nama_tanaman(self) -> str | None:
        return self.plant.nama if self.plant else None

    @property
    def varietas(self) -> str | None:
        return self.plant.varietas if self.plant else None
