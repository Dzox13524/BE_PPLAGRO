"""Shared enumerations - mengikuti ERD `hidroponik_selada` (nilai lowercase)."""
from enum import Enum


class UserRole(str, Enum):
    owner = "owner"          # Pemilik Mitra
    karyawan = "karyawan"    # Staf Operasional Kebun


class PlantStatus(str, Enum):
    pembibitan = "pembibitan"
    pertumbuhan = "pertumbuhan"
    siap_panen = "siap_panen"
    dipanen = "dipanen"
    mati = "mati"


ACTIVE_PLANT_STATUSES = (PlantStatus.pembibitan, PlantStatus.pertumbuhan, PlantStatus.siap_panen)


class InventoryType(str, Enum):
    bibit = "bibit"
    nutrisi = "nutrisi"
    lainnya = "lainnya"


class FinancialType(str, Enum):
    pemasukan = "pemasukan"
    pengeluaran = "pengeluaran"


class StockMovementType(str, Enum):
    masuk = "masuk"
    keluar = "keluar"


class PlantPart(str, Enum):
    daun = "daun"
    akar = "akar"
    seluruh_tanaman = "seluruh_tanaman"
