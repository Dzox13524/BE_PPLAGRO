"""Schemas `plants`, `growth_records`, dan Growth Chart - sesuai ERD `hidroponik_selada`."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.common.enums import ACTIVE_PLANT_STATUSES, PlantStatus


# ============================== Plant (`plants`) ==============================
class PlantCreate(BaseModel):
    kode_tanaman: str | None = Field(
        None, max_length=50, description="Kosongkan untuk generate otomatis (mis. SLD-20261104-XXXX)",
        examples=[None],
    )
    nama: str = Field("Selada", min_length=2, max_length=100)
    varietas: str | None = Field(None, max_length=100, examples=["Grand Rapids"])
    tanggal_tanam: date = Field(default_factory=date.today)
    tanggal_panen: date | None = Field(None, description="Tanggal panen (perkiraan / aktual)")
    status: PlantStatus = PlantStatus.pembibitan
    keterangan: str | None = Field(None, examples=["Greenhouse A - Rak 1 (120 lubang NFT)"])

    # Opsional: pemakaian bibit dari `inventory_items` -> otomatis catat `stock_movements` (keluar)
    bibit_inventory_id: int | None = Field(
        None, description="Opsional: ID `inventory_items` (jenis=bibit) yang dipakai"
    )
    jumlah_bibit_dipakai: float | None = Field(
        None, gt=0, description="Opsional: jumlah bibit dipakai -> otomatis mengurangi stok"
    )

    @model_validator(mode="after")
    def _validate(self) -> "PlantCreate":
        if self.tanggal_panen and self.tanggal_panen < self.tanggal_tanam:
            raise ValueError("tanggal_panen tidak boleh sebelum tanggal_tanam")
        if self.jumlah_bibit_dipakai and not self.bibit_inventory_id:
            raise ValueError("bibit_inventory_id wajib diisi jika jumlah_bibit_dipakai diisi")
        return self


class PlantUpdate(BaseModel):
    kode_tanaman: str | None = Field(None, max_length=50)
    nama: str | None = Field(None, min_length=2, max_length=100)
    varietas: str | None = Field(None, max_length=100)
    tanggal_tanam: date | None = None
    tanggal_panen: date | None = None
    status: PlantStatus | None = None
    keterangan: str | None = None


# ======================= Growth Record (`growth_records`) =======================
class GrowthRecordCreate(BaseModel):
    tanggal_pengamatan: datetime = Field(default_factory=datetime.utcnow)
    umur_tanaman: int | None = Field(None, ge=0, le=365, description="Kosongkan -> dihitung dari tanggal_tanam")

    # Parameter morfologi
    tinggi_cm: float | None = Field(None, ge=0, le=100, examples=[12.5])
    jumlah_daun: int | None = Field(None, ge=0, le=200, examples=[8])
    berat_gram: float | None = Field(None, ge=0, le=5000, examples=[65.0])

    # Parameter air dan lingkungan
    ph_air: float | None = Field(None, ge=0, le=14, examples=[6.0])
    suhu_air: float | None = Field(None, ge=0, le=50, examples=[22.0])
    ec: float | None = Field(None, ge=0, le=20, description="Electrical Conductivity (mS/cm)", examples=[1.4])
    suhu_c: float | None = Field(None, ge=-10, le=60, description="Suhu udara (°C)", examples=[25.0])
    kelembapan_persen: float | None = Field(None, ge=0, le=100, examples=[70.0])
    intensitas_cahaya: float | None = Field(None, ge=0, examples=[15000.0])

    # Pelacakan dataset eksternal
    sumber_data: str | None = Field("internal", max_length=150)
    source_record_id: str | None = Field(None, max_length=150)

    catatan: str | None = None


class GrowthRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plant_id: int
    recorded_by: int | None = None
    recorded_by_nama: str | None = None
    tanggal_pengamatan: datetime
    umur_tanaman: int | None = None

    tinggi_cm: float | None = None
    jumlah_daun: int | None = None
    berat_gram: float | None = None

    ph_air: float | None = None
    suhu_air: float | None = None
    ec: float | None = None
    suhu_c: float | None = None
    kelembapan_persen: float | None = None
    intensitas_cahaya: float | None = None

    sumber_data: str | None = None
    source_record_id: str | None = None
    catatan: str | None = None
    created_at: datetime | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ppm_estimasi(self) -> float | None:
        """Konversi bantu `ec` (mS/cm) -> PPM (skala 700) untuk kemudahan tampilan frontend."""
        return round(self.ec * 700.0, 1) if self.ec is not None else None


class PlantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    created_by_nama: str | None = None
    kode_tanaman: str
    nama: str
    varietas: str | None = None
    tanggal_tanam: date
    tanggal_panen: date | None = None
    status: PlantStatus
    keterangan: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    latest_growth_record: GrowthRecordOut | None = None
    growth_record_count: int = 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def umur_hari(self) -> int:
        end = self.tanggal_panen if self.status == PlantStatus.dipanen and self.tanggal_panen else date.today()
        return max(0, (end - self.tanggal_tanam).days)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def hari_menuju_panen(self) -> int | None:
        if self.tanggal_panen is None or self.status not in ACTIVE_PLANT_STATUSES:
            return None
        return (self.tanggal_panen - date.today()).days


class PlantDetailOut(PlantOut):
    pass


# ============================ Growth Chart ============================
class ChartDataset(BaseModel):
    key: str
    label: str
    unit: str
    data: list[float | None]
    borderColor: str
    backgroundColor: str
    yAxisID: str
    borderDash: list[int] | None = None


class GrowthChartOut(BaseModel):
    plant_id: int
    kode_tanaman: str
    varietas: str | None
    tanggal_tanam: date
    label_mode: str
    labels: list[str] = Field(..., description="Label sumbu-X siap pakai (Chart.js / ApexCharts)")
    dates: list[datetime]
    days_after_planting: list[int]
    datasets: list[ChartDataset]
    series: dict[str, list[float | None]] = Field(
        ...,
        description="Time-series: tinggi_cm, jumlah_daun, berat_gram, ec, ppm_level, ph_air (+ alias height_cm, leaf_count)",
    )
