"""Schemas Manajemen Inventaris (`inventory_items`) & Pergerakan Stok (`stock_movements`) - sesuai ERD."""
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from app.common.enums import InventoryType, PlantStatus, StockMovementType


def _to_float(v: Decimal | float | None) -> float | None:
    return float(v) if v is not None else None


class StockCreate(BaseModel):
    """Tambah barang inventaris (`inventory_items`). Bila `jumlah_stok > 0`, otomatis tercatat
    pergerakan `masuk` di `stock_movements`."""

    nama_barang: str = Field(..., min_length=2, max_length=150, examples=["Bibit Selada Grand Rapids"])
    jenis: InventoryType = Field(..., examples=["bibit"])
    satuan: str = Field(..., min_length=1, max_length=30, examples=["biji"])
    jumlah_stok: float = Field(0, ge=0, examples=[500])
    stok_minimum: float | None = Field(0, ge=0, examples=[100])
    keterangan: str | None = None


class StockUpdate(BaseModel):
    """Edit barang inventaris dan/atau catat pergerakan stok (`masuk` / `keluar`) ke `stock_movements`.

    Cara mengubah stok (pilih salah satu):
    1. `jenis_pergerakan` (`masuk` / `keluar`) + `jumlah` (> 0), atau
    2. `jumlah_stok` (set nilai akhir baru; otomatis dihitung selisihnya sebagai `masuk` / `keluar`).
    """

    nama_barang: str | None = Field(None, min_length=2, max_length=150)
    jenis: InventoryType | None = None
    satuan: str | None = Field(None, min_length=1, max_length=30)
    stok_minimum: float | None = Field(None, ge=0)
    keterangan: str | None = None

    # Pergerakan stok
    jenis_pergerakan: StockMovementType | None = Field(None, description="`masuk` atau `keluar`")
    jumlah: float | None = Field(None, gt=0, description="Jumlah pergerakan stok (> 0)", examples=[200])
    jumlah_stok: float | None = Field(None, ge=0, description="Alternatif: set jumlah_stok akhir langsung")
    tanggal: datetime | None = Field(None, description="Waktu pergerakan (default: sekarang)")
    keterangan_pergerakan: str | None = Field(None, description="Keterangan pada `stock_movements`",
                                              examples=["Restock dari supplier"])

    @model_validator(mode="after")
    def _validate_movement(self) -> "StockUpdate":
        if (self.jenis_pergerakan is None) ^ (self.jumlah is None):
            raise ValueError("'jenis_pergerakan' dan 'jumlah' harus diisi bersamaan")
        if self.jenis_pergerakan is not None and self.jumlah_stok is not None:
            raise ValueError("Gunakan salah satu: ('jenis_pergerakan' + 'jumlah') atau 'jumlah_stok'")
        return self


class StockMovementCreate(BaseModel):
    jenis_pergerakan: StockMovementType = Field(..., examples=["masuk"])
    jumlah: float = Field(..., gt=0, examples=[100])
    tanggal: datetime = Field(default_factory=datetime.utcnow)
    keterangan: str | None = Field(None, examples=["Penambahan stok nutrisi"])


class StockMovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_item_id: int
    nama_barang: str | None = None
    satuan: str | None = None
    jenis_barang: str | None = None
    recorded_by: int
    recorded_by_nama: str | None = None
    jenis_pergerakan: StockMovementType
    jumlah: float
    tanggal: datetime
    keterangan: str | None = None
    created_at: datetime | None = None


class StockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nama_barang: str
    jenis: InventoryType
    satuan: str
    jumlah_stok: float
    stok_minimum: float | None = 0
    keterangan: str | None = None
    created_by: int
    created_by_nama: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_low_stock(self) -> bool:
        return self.jumlah_stok <= (self.stok_minimum or 0)


class StockDetailOut(StockOut):
    movements: list[StockMovementOut] = []


# ------------------------- Planted overview -------------------------
class LatestGrowthBrief(BaseModel):
    tanggal_pengamatan: datetime
    umur_tanaman: int | None
    tinggi_cm: float | None = None
    jumlah_daun: int | None = None
    berat_gram: float | None = None
    ph_air: float | None = None
    ec: float | None = None


class PlantedBatchBrief(BaseModel):
    id: int
    kode_tanaman: str
    nama: str
    varietas: str | None
    status: PlantStatus
    tanggal_tanam: date
    umur_hari: int
    tanggal_panen: date | None
    hari_menuju_panen: int | None
    keterangan: str | None = None
    latest_growth: LatestGrowthBrief | None = None


class PlantedOverviewOut(BaseModel):
    total_active_plants: int
    by_status: dict[str, int]
    by_varietas: dict[str, int]
    upcoming_harvest_7_days: list[PlantedBatchBrief]
    overdue_harvest: list[PlantedBatchBrief]
    plants: list[PlantedBatchBrief]
    stock_summary: dict[str, int]
