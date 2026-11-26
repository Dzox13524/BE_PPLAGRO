"""Schemas AI 2 - Diagnosis Kesehatan Tanaman (`diagnosis_records`) sesuai ERD `hidroponik_selada`."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.common.enums import PlantPart
from app.modules.knowledge_base.schemas import DiseaseInfoOut, NutritionConditionOut
from app.utils.file_handler import build_public_url


class DiagnosisOut(BaseModel):
    """Representasi lengkap baris `diagnosis_records` beserta relasi `disease_infos` & `nutrition_conditions`,
    serta field ringkasan (`diagnosis_result`, `nutrient_condition`, `disease_info`, `plant_condition_summary`)
    sesuai kontrak prompt untuk Frontend Laravel."""

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    # Kolom asli tabel `diagnosis_records` (ERD)
    id: int
    plant_id: int
    kode_tanaman: str | None = None
    nama_tanaman: str | None = None
    varietas: str | None = None
    diagnosed_by: int | None = None
    diagnosed_by_nama: str | None = None
    tanggal_diagnosis: datetime
    image_path: str
    plant_part: PlantPart | None = None
    kelas_diagnosis: str
    confidence: float | None = None
    disease_info_id: int | None = None
    nutrition_condition_id: int | None = None
    model: str
    versi_model: str | None = None
    sumber_data: str | None = None
    keterangan: str | None = None
    rekomendasi: str | None = None
    created_at: datetime | None = None

    # Objek relasi basis pengetahuan
    disease_info_rel: DiseaseInfoOut | None = None
    nutrition_condition_rel: NutritionConditionOut | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def image_url(self) -> str | None:
        return build_public_url(self.image_path)

    # ---- Field kontrak prompt (kompatibilitas langsung untuk Laravel) ----
    @computed_field  # type: ignore[prop-decorator]
    @property
    def diagnosis_result(self) -> str:
        return self.disease_info_rel.nama_penyakit if self.disease_info_rel else self.kelas_diagnosis

    @computed_field  # type: ignore[prop-decorator]
    @property
    def nutrient_condition(self) -> str:
        if self.nutrition_condition_rel:
            nc = self.nutrition_condition_rel
            unsur = f" ({nc.unsur_nutrisi})" if nc.unsur_nutrisi else ""
            return f"{nc.nama_kondisi}{unsur}: {nc.deskripsi or ''}".strip(": ")
        return "Normal"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def disease_info(self) -> str:
        if self.disease_info_rel:
            di = self.disease_info_rel
            parts = [p for p in (di.deskripsi, f"Gejala: {di.gejala}" if di.gejala else None) if p]
            return " ".join(parts)
        return self.keterangan or ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def plant_condition_summary(self) -> str:
        parts = [p for p in (self.keterangan, self.rekomendasi) if p]
        return " ".join(parts)


class DiagnosisListItem(BaseModel):
    """Item ringkas untuk `GET /diagnosis/history`."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: int
    kode_tanaman: str | None = None
    nama_tanaman: str | None = None
    varietas: str | None = None
    tanggal_diagnosis: datetime
    image_path: str
    plant_part: PlantPart | None = None
    kelas_diagnosis: str
    confidence: float | None = None
    disease_info_id: int | None = None
    nutrition_condition_id: int | None = None
    model: str
    versi_model: str | None = None
    keterangan: str | None = None
    rekomendasi: str | None = None
    diagnosed_by_nama: str | None = None
    created_at: datetime | None = None
    disease_info_rel: DiseaseInfoOut | None = None
    nutrition_condition_rel: NutritionConditionOut | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def image_url(self) -> str | None:
        return build_public_url(self.image_path)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def diagnosis_result(self) -> str:
        return self.disease_info_rel.nama_penyakit if self.disease_info_rel else self.kelas_diagnosis

    @computed_field  # type: ignore[prop-decorator]
    @property
    def nutrient_condition(self) -> str:
        return self.nutrition_condition_rel.nama_kondisi if self.nutrition_condition_rel else "Normal"
