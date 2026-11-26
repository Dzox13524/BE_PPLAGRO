"""Manajemen Stok Bibit & Nutrisi (`inventory_items` & `stock_movements`) - OWNER ONLY."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.common.enums import InventoryType
from app.common.responses import COMMON_ERROR_RESPONSES, APIResponse, pagination_meta, success_response
from app.core.database import get_db
from app.core.dependencies import require_owner
from app.modules.employees.models import User
from app.modules.stocks import service
from app.modules.stocks.schemas import (
    PlantedOverviewOut,
    StockCreate,
    StockDetailOut,
    StockMovementCreate,
    StockMovementOut,
    StockOut,
    StockUpdate,
)

router = APIRouter(
    prefix="/stocks",
    tags=["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
    dependencies=[Depends(require_owner)],
    responses=COMMON_ERROR_RESPONSES,
)


@router.get("/planted-overview", response_model=APIResponse[PlantedOverviewOut],
            summary="Ringkasan tanaman selada yang sedang ditanam")
def planted_overview(db: Session = Depends(get_db)):
    return success_response(PlantedOverviewOut(**service.planted_overview(db)), "Ringkasan tanaman yang ditanam")


@router.post("", response_model=APIResponse[StockOut], status_code=status.HTTP_201_CREATED,
             summary="Tambah stok barang inventaris (`bibit` / `nutrisi` / `lainnya`)")
def create_stock(payload: StockCreate, db: Session = Depends(get_db), user: User = Depends(require_owner)):
    item = service.create_stock(db, payload, user)
    return success_response(StockOut.model_validate(item), "Stok berhasil ditambahkan")


@router.get("", response_model=APIResponse[list[StockOut]], summary="Lihat stok barang yang tersedia")
def list_stocks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    jenis: InventoryType | None = Query(None, description="Filter: bibit | nutrisi | lainnya"),
    search: str | None = Query(None, description="Cari nama_barang / keterangan"),
    low_stock_only: bool = Query(False, description="Hanya stok yang <= stok_minimum"),
    available_only: bool = Query(False, description="Hanya stok dengan jumlah_stok > 0"),
    db: Session = Depends(get_db),
):
    items, total = service.list_stocks(
        db, page=page, per_page=per_page, jenis=jenis, search=search,
        low_stock_only=low_stock_only, available_only=available_only,
    )
    return success_response(
        [StockOut.model_validate(s) for s in items],
        "Daftar stok berhasil diambil",
        pagination_meta(page, per_page, total, summary=service.stock_summary(db)),
    )


@router.get("/movements", response_model=APIResponse[list[StockMovementOut]],
            summary="Riwayat pergerakan stok terbaru (`stock_movements`)")
def list_recent_movements(
    limit: int = Query(30, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows = service.list_movements(db, limit=limit)
    return success_response([StockMovementOut.model_validate(m) for m in rows], "Riwayat pergerakan stok")


@router.get("/{stock_id}", response_model=APIResponse[StockDetailOut],
            summary="Detail barang inventaris + riwayat pergerakan (`stock_movements`)")
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    return success_response(StockDetailOut.model_validate(service.get_stock(db, stock_id)), "Detail stok")


@router.put("/{stock_id}", response_model=APIResponse[StockDetailOut],
            summary="Edit barang inventaris & catat pergerakan stok (`masuk` / `keluar`)")
def update_stock(stock_id: int, payload: StockUpdate, db: Session = Depends(get_db),
                 user: User = Depends(require_owner)):
    item = service.update_stock(db, stock_id, payload, user)
    return success_response(StockDetailOut.model_validate(item), "Stok berhasil diperbarui")


@router.post("/{stock_id}/movements", response_model=APIResponse[StockMovementOut],
             status_code=status.HTTP_201_CREATED, summary="Catat pergerakan stok (`masuk` / `keluar`)")
def add_movement(stock_id: int, payload: StockMovementCreate, db: Session = Depends(get_db),
                 user: User = Depends(require_owner)):
    mv = service.add_movement(db, stock_id, payload, user)
    return success_response(StockMovementOut.model_validate(mv), "Pergerakan stok berhasil dicatat")


@router.delete("/{stock_id}", response_model=APIResponse[None],
               summary="Hapus barang inventaris (`inventory_items`)")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    service.delete_stock(db, stock_id)
    return success_response(None, "Stok berhasil dihapus")
