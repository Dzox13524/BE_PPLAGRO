"""Business logic Manajemen Inventaris (`inventory_items`) & `stock_movements` + ringkasan tanaman aktif."""
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.enums import ACTIVE_PLANT_STATUSES, InventoryType, StockMovementType
from app.common.exceptions import AppException, NotFoundException
from app.common.time import utcnow
from app.modules.employees.models import User
from app.modules.plants.models import GrowthRecord, Plant
from app.modules.stocks.models import InventoryItem, StockMovement
from app.modules.stocks.schemas import StockCreate, StockMovementCreate, StockUpdate


def list_stocks(
    db: Session, *, page: int, per_page: int, jenis: InventoryType | None = None,
    search: str | None = None, low_stock_only: bool = False, available_only: bool = False,
) -> tuple[list[InventoryItem], int]:
    stmt = select(InventoryItem)
    if jenis:
        stmt = stmt.where(InventoryItem.jenis == jenis)
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(or_(InventoryItem.nama_barang.ilike(like), InventoryItem.keterangan.ilike(like)))
    if low_stock_only:
        stmt = stmt.where(InventoryItem.jumlah_stok <= func.coalesce(InventoryItem.stok_minimum, 0))
    if available_only:
        stmt = stmt.where(InventoryItem.jumlah_stok > 0)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(InventoryItem.jenis, InventoryItem.nama_barang).offset((page - 1) * per_page).limit(per_page)
    ).unique().all()
    return list(items), total


def stock_summary(db: Session) -> dict[str, int]:
    def count(*conds) -> int:
        return db.scalar(select(func.count(InventoryItem.id)).where(*conds)) or 0

    return {
        "total_items": count(),
        "bibit_items": count(InventoryItem.jenis == InventoryType.bibit),
        "nutrisi_items": count(InventoryItem.jenis == InventoryType.nutrisi),
        "lainnya_items": count(InventoryItem.jenis == InventoryType.lainnya),
        "low_stock_items": count(InventoryItem.jumlah_stok <= func.coalesce(InventoryItem.stok_minimum, 0)),
        "out_of_stock_items": count(InventoryItem.jumlah_stok <= 0),
    }


def get_stock(db: Session, item_id: int) -> InventoryItem:
    item = db.get(InventoryItem, item_id)
    if item is None:
        raise NotFoundException(f"Barang inventaris dengan id {item_id} tidak ditemukan.")
    return item


def create_stock(db: Session, data: StockCreate, user: User) -> InventoryItem:
    qty = Decimal(str(data.jumlah_stok))
    min_qty = Decimal(str(data.stok_minimum or 0))
    item = InventoryItem(
        nama_barang=data.nama_barang.strip(),
        jenis=data.jenis,
        satuan=data.satuan.strip(),
        jumlah_stok=qty,
        stok_minimum=min_qty,
        keterangan=data.keterangan,
        created_by=user.id,
    )
    db.add(item)
    db.flush()

    if qty > 0:
        db.add(StockMovement(
            inventory_item_id=item.id,
            recorded_by=user.id,
            jenis_pergerakan=StockMovementType.masuk,
            jumlah=qty,
            tanggal=utcnow(),
            keterangan=data.keterangan or "Stok awal",
        ))
    db.commit()
    db.refresh(item)
    return item


def record_movement(
    db: Session, item: InventoryItem, *, jenis_pergerakan: StockMovementType, jumlah: Decimal,
    user: User, tanggal=None, keterangan: str | None = None, commit: bool = True,
) -> StockMovement:
    current = Decimal(str(item.jumlah_stok or 0))
    if jenis_pergerakan == StockMovementType.keluar:
        if current < jumlah:
            raise AppException(
                f"Stok '{item.nama_barang}' tidak mencukupi. Tersedia {current:g} {item.satuan}, "
                f"pengeluaran {jumlah:g} {item.satuan}.", 400,
            )
        item.jumlah_stok = current - jumlah
    else:
        item.jumlah_stok = current + jumlah

    mv = StockMovement(
        inventory_item_id=item.id,
        recorded_by=user.id,
        jenis_pergerakan=jenis_pergerakan,
        jumlah=jumlah,
        tanggal=tanggal or utcnow(),
        keterangan=keterangan,
    )
    db.add(mv)
    if commit:
        db.commit()
        db.refresh(mv)
    else:
        db.flush()
    return mv


def update_stock(db: Session, item_id: int, data: StockUpdate, user: User) -> InventoryItem:
    item = get_stock(db, item_id)
    payload = data.model_dump(exclude_unset=True)

    jenis_pergerakan = payload.pop("jenis_pergerakan", None)
    jumlah = payload.pop("jumlah", None)
    new_jumlah_stok = payload.pop("jumlah_stok", None)
    tanggal = payload.pop("tanggal", None)
    ket_mv = payload.pop("keterangan_pergerakan", None)

    for key in ("nama_barang", "jenis", "satuan", "stok_minimum", "keterangan"):
        if key in payload and payload[key] is not None:
            val = Decimal(str(payload[key])) if key == "stok_minimum" else payload[key]
            setattr(item, key, val)

    if jenis_pergerakan is not None and jumlah is not None:
        record_movement(
            db, item, jenis_pergerakan=jenis_pergerakan, jumlah=Decimal(str(jumlah)),
            user=user, tanggal=tanggal, keterangan=ket_mv or data.keterangan, commit=False,
        )
    elif new_jumlah_stok is not None:
        target = Decimal(str(new_jumlah_stok))
        current = Decimal(str(item.jumlah_stok or 0))
        diff = target - current
        if diff != 0:
            record_movement(
                db, item,
                jenis_pergerakan=StockMovementType.masuk if diff > 0 else StockMovementType.keluar,
                jumlah=abs(diff), user=user, tanggal=tanggal,
                keterangan=ket_mv or "Penyesuaian jumlah stok", commit=False,
            )

    db.commit()
    db.refresh(item)
    return item


def add_movement(db: Session, item_id: int, data: StockMovementCreate, user: User) -> StockMovement:
    item = get_stock(db, item_id)
    return record_movement(
        db, item, jenis_pergerakan=data.jenis_pergerakan, jumlah=Decimal(str(data.jumlah)),
        user=user, tanggal=data.tanggal, keterangan=data.keterangan, commit=True,
    )


def delete_stock(db: Session, item_id: int) -> None:
    item = get_stock(db, item_id)
    db.delete(item)
    db.commit()


def list_movements(db: Session, *, limit: int = 30) -> list[StockMovement]:
    return list(
        db.scalars(
            select(StockMovement)
            .order_by(StockMovement.tanggal.desc(), StockMovement.id.desc())
            .limit(limit)
        ).unique().all()
    )


# --------------------------------------------------------- planted overview
def planted_overview(db: Session) -> dict[str, Any]:
    today = date.today()
    plants = db.scalars(
        select(Plant).where(Plant.status.in_(ACTIVE_PLANT_STATUSES)).order_by(Plant.tanggal_tanam)
    ).unique().all()

    latest_records: dict[int, GrowthRecord] = {}
    if plants:
        ids = [p.id for p in plants]
        for rec in db.scalars(
            select(GrowthRecord)
            .where(GrowthRecord.plant_id.in_(ids))
            .order_by(GrowthRecord.tanggal_pengamatan, GrowthRecord.id)
        ).unique():
            latest_records[rec.plant_id] = rec

    by_status: dict[str, int] = {s.value: 0 for s in ACTIVE_PLANT_STATUSES}
    by_varietas: dict[str, int] = {}
    batches, upcoming, overdue = [], [], []

    for p in plants:
        by_status[p.status.value] = by_status.get(p.status.value, 0) + 1
        varietas = p.varietas or "Tidak diketahui"
        by_varietas[varietas] = by_varietas.get(varietas, 0) + 1

        days_to_harvest = (p.tanggal_panen - today).days if p.tanggal_panen else None
        rec = latest_records.get(p.id)
        brief = {
            "id": p.id,
            "kode_tanaman": p.kode_tanaman,
            "nama": p.nama,
            "varietas": p.varietas,
            "status": p.status,
            "tanggal_tanam": p.tanggal_tanam,
            "umur_hari": max(0, (today - p.tanggal_tanam).days),
            "tanggal_panen": p.tanggal_panen,
            "hari_menuju_panen": days_to_harvest,
            "keterangan": p.keterangan,
            "latest_growth": {
                "tanggal_pengamatan": rec.tanggal_pengamatan,
                "umur_tanaman": rec.umur_tanaman,
                "tinggi_cm": float(rec.tinggi_cm) if rec.tinggi_cm is not None else None,
                "jumlah_daun": rec.jumlah_daun,
                "berat_gram": float(rec.berat_gram) if rec.berat_gram is not None else None,
                "ph_air": float(rec.ph_air) if rec.ph_air is not None else None,
                "ec": float(rec.ec) if rec.ec is not None else None,
            } if rec else None,
        }
        batches.append(brief)
        if days_to_harvest is not None:
            if 0 <= days_to_harvest <= 7:
                upcoming.append(brief)
            elif days_to_harvest < 0:
                overdue.append(brief)

    return {
        "total_active_plants": len(plants),
        "by_status": by_status,
        "by_varietas": by_varietas,
        "upcoming_harvest_7_days": upcoming,
        "overdue_harvest": overdue,
        "plants": batches,
        "stock_summary": stock_summary(db),
    }
