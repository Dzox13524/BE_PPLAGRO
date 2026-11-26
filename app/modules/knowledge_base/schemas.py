"""Schemas `disease_infos` & `nutrition_conditions` (Basis Pengetahuan)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DiseaseInfoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nama_penyakit: str
    deskripsi: str | None = None
    gejala: str | None = None
    penanganan_awal: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class NutritionConditionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nama_kondisi: str
    unsur_nutrisi: str | None = None
    deskripsi: str | None = None
    gejala: str | None = None
    penanganan_awal: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

