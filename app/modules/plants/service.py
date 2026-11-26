"""Business logic `plants`, `growth_records`, & Growth Chart generator."""
import math
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.enums import InventoryType, PlantStatus, StockMovementType
from app.common.exceptions import AppException, ConflictException, NotFoundException
from app.modules.employees.models import User
from app.modules.plants.models import GrowthRecord, Plant
from app.modules.plants.schemas import GrowthRecordCreate, PlantCreate, PlantUpdate
from app.modules.stocks import service as stock_service

DEFAULT_GROWING_DAYS = 40


def _logistic(t: float, vmax: float, k: float, mid: float) -> float:
    return vmax / (1.0 + math.exp(-k * (t - mid)))


def reference_height(age_days: float) -> float:
    """Kurva referensi tinggi selada hidroponik (cm) per HST."""
    return _logistic(age_days, 25.0, 0.15, 22.0)


def reference_leaves(age_days: float) -> float:
    """Kurva referensi jumlah daun selada hidroponik per HST."""
    return _logistic(age_days, 18.0, 0.13, 18.0)


def reference_weight(age_days: float) -> float:
    """Kurva referensi berat selada hidroponik (gram) per HST."""
    return _logistic(age_days, 220.0, 0.16, 32.0)


def _dec(val: float | None) -> Decimal | None:
    return Decimal(str(val)) if val is not None else None


def _flt(val: Decimal | float | None) -> float | None:
    return float(val) if val is not None else None


def _generate_kode_tanaman(db: Session, tanggal_tanam: date) -> str:
    while True:
        code = f"SLD-{tanggal_tanam:%Y%m%d}-{uuid.uuid4().hex[:4].upper()}"
        if db.scalar(select(Plant.id).where(Plant.kode_tanaman == code)) is None:
            return code


def _ensure_unique_kode(db: Session, kode: str, exclude_id: int | None = None) -> None:
    stmt = select(Plant.id).where(Plant.kode_tanaman == kode)
    if exclude_id:
        stmt = stmt.where(Plant.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise ConflictException(f"Kode tanaman '{kode}' sudah digunakan.")


def compute_umur_tanaman(plant: Plant, on_dt: datetime | date | None = None) -> int:
    d = on_dt.date() if isinstance(on_dt, datetime) else (on_dt or date.today())
    return max(0, (d - plant.tanggal_tanam).days)


# --------------------------------------------------------------------- CRUD
def list_plants(
    db: Session, *, page: int, per_page: int, status: PlantStatus | None = None, search: str | None = None
) -> tuple[list[Plant], int]:
    stmt = select(Plant)
    if status:
        stmt = stmt.where(Plant.status == status)
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(or_(Plant.kode_tanaman.ilike(like), Plant.nama.ilike(like),
                              Plant.varietas.ilike(like), Plant.keterangan.ilike(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(Plant.tanggal_tanam.desc(), Plant.id.desc()).offset((page - 1) * per_page).limit(per_page)
    ).unique().all()
    return list(items), total


def get_plant(db: Session, plant_id: int) -> Plant:
    plant = db.get(Plant, plant_id)
    if plant is None:
        raise NotFoundException(f"Data tanaman dengan id {plant_id} tidak ditemukan.")
    return plant


def create_plant(db: Session, data: PlantCreate, user: User) -> Plant:
    if data.kode_tanaman:
        _ensure_unique_kode(db, data.kode_tanaman)
    kode = data.kode_tanaman or _generate_kode_tanaman(db, data.tanggal_tanam)

    plant = Plant(
        created_by=user.id,
        kode_tanaman=kode,
        nama=data.nama,
        varietas=data.varietas,
        tanggal_tanam=data.tanggal_tanam,
        tanggal_panen=data.tanggal_panen or (data.tanggal_tanam + timedelta(days=DEFAULT_GROWING_DAYS)),
        status=data.status,
        keterangan=data.keterangan,
    )

    if data.bibit_inventory_id:
        item = stock_service.get_stock(db, data.bibit_inventory_id)
        if item.jenis != InventoryType.bibit:
            raise AppException("bibit_inventory_id harus merujuk ke inventaris dengan jenis='bibit'.", 400)
        if data.jumlah_bibit_dipakai:
            stock_service.record_movement(
                db, item,
                jenis_pergerakan=StockMovementType.keluar,
                jumlah=Decimal(str(data.jumlah_bibit_dipakai)),
                user=user,
                keterangan=f"Pemakaian bibit untuk tanaman {kode}",
                commit=False,
            )

    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


def update_plant(db: Session, plant_id: int, data: PlantUpdate) -> Plant:
    plant = get_plant(db, plant_id)
    payload = data.model_dump(exclude_unset=True)

    if payload.get("kode_tanaman"):
        _ensure_unique_kode(db, payload["kode_tanaman"], exclude_id=plant.id)

    for key, value in payload.items():
        if key in ("kode_tanaman", "nama", "tanggal_tanam", "status") and value is None:
            continue
        setattr(plant, key, value)

    if plant.tanggal_panen and plant.tanggal_panen < plant.tanggal_tanam:
        raise AppException("tanggal_panen tidak boleh sebelum tanggal_tanam", 422)
    if plant.status == PlantStatus.dipanen and plant.tanggal_panen is None:
        plant.tanggal_panen = date.today()

    db.commit()
    db.refresh(plant)
    return plant


def delete_plant(db: Session, plant_id: int) -> None:
    plant = get_plant(db, plant_id)
    db.delete(plant)
    db.commit()


# ------------------------------------------------------------ growth records
def add_growth_record(
    db: Session, plant: Plant, data: GrowthRecordCreate, user: User, commit: bool = True
) -> GrowthRecord:
    if data.tanggal_pengamatan.date() < plant.tanggal_tanam:
        raise AppException("tanggal_pengamatan tidak boleh sebelum tanggal_tanam.", 422)
    umur = data.umur_tanaman if data.umur_tanaman is not None else compute_umur_tanaman(plant, data.tanggal_pengamatan)

    rec = GrowthRecord(
        plant_id=plant.id,
        recorded_by=user.id,
        tanggal_pengamatan=data.tanggal_pengamatan,
        umur_tanaman=umur,
        tinggi_cm=_dec(data.tinggi_cm),
        jumlah_daun=data.jumlah_daun,
        berat_gram=_dec(data.berat_gram),
        ph_air=_dec(data.ph_air),
        suhu_air=_dec(data.suhu_air),
        ec=_dec(data.ec),
        suhu_c=_dec(data.suhu_c),
        kelembapan_persen=_dec(data.kelembapan_persen),
        intensitas_cahaya=_dec(data.intensitas_cahaya),
        sumber_data=data.sumber_data,
        source_record_id=data.source_record_id,
        catatan=data.catatan,
    )
    # Otomatis naikkan status pembibitan -> pertumbuhan setelah 14 HST
    if plant.status == PlantStatus.pembibitan and umur >= 14:
        plant.status = PlantStatus.pertumbuhan

    db.add(rec)
    if commit:
        db.commit()
        db.refresh(rec)
    else:
        db.flush()
    return rec


def get_growth_records(db: Session, plant_id: int) -> list[GrowthRecord]:
    get_plant(db, plant_id)
    return list(db.scalars(
        select(GrowthRecord)
        .where(GrowthRecord.plant_id == plant_id)
        .order_by(GrowthRecord.tanggal_pengamatan, GrowthRecord.id)
    ).unique().all())


def get_growth_record(db: Session, plant_id: int, record_id: int) -> GrowthRecord:
    get_plant(db, plant_id)
    rec = db.scalar(
        select(GrowthRecord).where(GrowthRecord.id == record_id, GrowthRecord.plant_id == plant_id)
    )
    if rec is None:
        raise NotFoundException(f"Catatan pertumbuhan id {record_id} untuk tanaman {plant_id} tidak ditemukan.")
    return rec


def update_growth_record(db: Session, plant_id: int, record_id: int, data: GrowthRecordCreate) -> GrowthRecord:
    plant = get_plant(db, plant_id)
    rec = get_growth_record(db, plant_id, record_id)
    if data.tanggal_pengamatan.date() < plant.tanggal_tanam:
        raise AppException("tanggal_pengamatan tidak boleh sebelum tanggal_tanam.", 422)

    rec.tanggal_pengamatan = data.tanggal_pengamatan
    rec.umur_tanaman = (
        data.umur_tanaman if data.umur_tanaman is not None else compute_umur_tanaman(plant, data.tanggal_pengamatan)
    )
    rec.tinggi_cm = _dec(data.tinggi_cm)
    rec.jumlah_daun = data.jumlah_daun
    rec.berat_gram = _dec(data.berat_gram)
    rec.ph_air = _dec(data.ph_air)
    rec.suhu_air = _dec(data.suhu_air)
    rec.ec = _dec(data.ec)
    rec.suhu_c = _dec(data.suhu_c)
    rec.kelembapan_persen = _dec(data.kelembapan_persen)
    rec.intensitas_cahaya = _dec(data.intensitas_cahaya)
    if data.catatan is not None:
        rec.catatan = data.catatan

    db.commit()
    db.refresh(rec)
    return rec


def delete_growth_record(db: Session, plant_id: int, record_id: int) -> None:
    rec = get_growth_record(db, plant_id, record_id)
    db.delete(rec)
    db.commit()


def growth_history_summary(records: list[GrowthRecord]) -> dict[str, Any]:
    if not records:
        return {"total_records": 0}
    first, last = records[0], records[-1]
    h_first = _flt(first.tinggi_cm) or 0.0
    h_last = _flt(last.tinggi_cm) or 0.0
    l_first = first.jumlah_daun or 0
    l_last = last.jumlah_daun or 0
    span = max(1, (last.umur_tanaman or 0) - (first.umur_tanaman or 0))
    return {
        "total_records": len(records),
        "first_record_at": first.tanggal_pengamatan.isoformat(),
        "last_record_at": last.tanggal_pengamatan.isoformat(),
        "tinggi_gain_cm": round(h_last - h_first, 2),
        "jumlah_daun_gain": l_last - l_first,
        "avg_daily_height_growth_cm": round((h_last - h_first) / span, 3) if len(records) > 1 else 0,
        "latest_tinggi_cm": _flt(last.tinggi_cm),
        "latest_jumlah_daun": last.jumlah_daun,
        "latest_berat_gram": _flt(last.berat_gram),
    }


# --------------------------------------------------------------- growth chart
def build_growth_chart(db: Session, plant_id: int, label_mode: str = "day", include_reference: bool = True) -> dict:
    plant = get_plant(db, plant_id)
    records = get_growth_records(db, plant_id)

    dates = [r.tanggal_pengamatan for r in records]
    days = [r.umur_tanaman if r.umur_tanaman is not None else compute_umur_tanaman(plant, r.tanggal_pengamatan)
            for r in records]
    labels = [d.strftime("%d %b %Y") for d in dates] if label_mode == "date" else [f"HST {d}" for d in days]

    def ds(key: str, label: str, unit: str, data: list, color: str, axis: str, dash: list[int] | None = None):
        return {
            "key": key, "label": label, "unit": unit, "data": data,
            "borderColor": color, "backgroundColor": color + "33", "yAxisID": axis, "borderDash": dash,
        }

    tinggi = [_flt(r.tinggi_cm) for r in records]
    daun = [float(r.jumlah_daun) if r.jumlah_daun is not None else None for r in records]
    berat = [_flt(r.berat_gram) for r in records]
    ec_list = [_flt(r.ec) for r in records]
    ppm_list = [round(float(r.ec) * 700.0, 1) if r.ec is not None else None for r in records]
    ph_list = [_flt(r.ph_air) for r in records]

    series: dict[str, list[float | None]] = {
        "tinggi_cm": tinggi,
        "jumlah_daun": daun,
        "berat_gram": berat,
        "ec": ec_list,
        "ppm_level": ppm_list,
        "ph_air": ph_list,
        # alias kompatibilitas Chart.js pada prompt
        "height_cm": tinggi,
        "leaf_count": daun,
    }
    datasets = [
        ds("height_cm", "Tinggi Tanaman", "cm", tinggi, "#22c55e", "y"),
        ds("leaf_count", "Jumlah Daun", "helai", daun, "#3b82f6", "y"),
        ds("berat_gram", "Berat Tanaman", "g", berat, "#06b6d4", "y"),
        ds("ec", "EC Nutrisi", "mS/cm", ec_list, "#10b981", "y2"),
        ds("ppm_level", "Nutrisi (PPM ~ EC×700)", "ppm", ppm_list, "#f59e0b", "y1"),
        ds("ph_air", "pH Air", "pH", ph_list, "#a855f7", "y2"),
    ]
    if include_reference:
        series["ideal_height_cm"] = [round(reference_height(max(d, 1)), 1) for d in days]
        datasets.append(ds("ideal_height_cm", "Tinggi Ideal (Referensi)", "cm",
                           series["ideal_height_cm"], "#94a3b8", "y", [6, 4]))

    return {
        "plant_id": plant.id,
        "kode_tanaman": plant.kode_tanaman,
        "varietas": plant.varietas,
        "tanggal_tanam": plant.tanggal_tanam,
        "label_mode": label_mode,
        "labels": labels,
        "dates": dates,
        "days_after_planting": days,
        "datasets": datasets,
        "series": series,
    }
