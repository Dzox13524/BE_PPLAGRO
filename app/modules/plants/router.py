"""Manajemen Tanaman (`plants`) & Catatan Pertumbuhan (`growth_records`) - KARYAWAN & OWNER."""
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.common.enums import PlantStatus
from app.common.responses import COMMON_ERROR_RESPONSES, APIResponse, pagination_meta, success_response
from app.core.database import get_db
from app.core.dependencies import require_karyawan
from app.modules.employees.models import User
from app.modules.plants import service
from app.modules.plants.schemas import (
    GrowthChartOut,
    GrowthRecordCreate,
    GrowthRecordOut,
    PlantCreate,
    PlantDetailOut,
    PlantOut,
    PlantUpdate,
)

router = APIRouter(
    prefix="/plants",
    tags=["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
    dependencies=[Depends(require_karyawan)],
    responses=COMMON_ERROR_RESPONSES,
)


@router.get("", response_model=APIResponse[list[PlantOut]], summary="Lihat semua data tanaman selada")
def list_plants(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: PlantStatus | None = Query(None, alias="status"),
    search: str | None = Query(None, description="Cari kode_tanaman / nama / varietas / keterangan"),
    db: Session = Depends(get_db),
):
    items, total = service.list_plants(db, page=page, per_page=per_page, status=status_filter, search=search)
    return success_response(
        [PlantOut.model_validate(p) for p in items], "Daftar tanaman berhasil diambil",
        pagination_meta(page, per_page, total),
    )


@router.post("", response_model=APIResponse[PlantOut], status_code=status.HTTP_201_CREATED,
             summary="Tambah data tanaman baru (`plants`)")
def create_plant(payload: PlantCreate, db: Session = Depends(get_db), user: User = Depends(require_karyawan)):
    plant = service.create_plant(db, payload, user)
    return success_response(PlantOut.model_validate(plant), "Data tanaman berhasil ditambahkan")


@router.get("/{plant_id}", response_model=APIResponse[PlantDetailOut], summary="Detail tanaman")
def get_plant(plant_id: int, db: Session = Depends(get_db)):
    plant = service.get_plant(db, plant_id)
    detail = PlantDetailOut.model_validate(plant)
    if plant.growth_records:
        detail.latest_growth_record = GrowthRecordOut.model_validate(plant.growth_records[-1])
        detail.growth_record_count = len(plant.growth_records)
    return success_response(detail, "Detail tanaman")


@router.put("/{plant_id}", response_model=APIResponse[PlantOut], summary="Update data tanaman")
def update_plant(plant_id: int, payload: PlantUpdate, db: Session = Depends(get_db)):
    plant = service.update_plant(db, plant_id, payload)
    return success_response(PlantOut.model_validate(plant), "Data tanaman berhasil diperbarui")


@router.delete("/{plant_id}", response_model=APIResponse[None], summary="Hapus data tanaman")
def delete_plant(plant_id: int, db: Session = Depends(get_db)):
    service.delete_plant(db, plant_id)
    return success_response(None, "Data tanaman berhasil dihapus")


@router.post("/{plant_id}/growth-records", response_model=APIResponse[GrowthRecordOut],
             status_code=status.HTTP_201_CREATED, summary="Tambah catatan pertumbuhan (`growth_records`)")
@router.post("/{plant_id}/growth-logs", response_model=APIResponse[GrowthRecordOut],
             status_code=status.HTTP_201_CREATED, include_in_schema=False)
def add_growth_record(plant_id: int, payload: GrowthRecordCreate, db: Session = Depends(get_db),
                      user: User = Depends(require_karyawan)):
    plant = service.get_plant(db, plant_id)
    rec = service.add_growth_record(db, plant, payload, user)
    return success_response(GrowthRecordOut.model_validate(rec), "Catatan pertumbuhan berhasil disimpan")


@router.get("/{plant_id}/growth-history", response_model=APIResponse[list[GrowthRecordOut]],
            summary="Riwayat catatan pertumbuhan (`growth_records`) secara kronologis")
def growth_history(plant_id: int, db: Session = Depends(get_db)):
    records = service.get_growth_records(db, plant_id)
    return success_response(
        [GrowthRecordOut.model_validate(r) for r in records],
        "Riwayat pertumbuhan berhasil diambil",
        service.growth_history_summary(records),
    )


@router.put("/{plant_id}/growth-records/{record_id}", response_model=APIResponse[GrowthRecordOut],
            summary="Perbarui catatan pertumbuhan (`growth_records`)")
def update_growth_record(plant_id: int, record_id: int, payload: GrowthRecordCreate, db: Session = Depends(get_db)):
    rec = service.update_growth_record(db, plant_id, record_id, payload)
    return success_response(GrowthRecordOut.model_validate(rec), "Catatan pertumbuhan berhasil diperbarui")


@router.delete("/{plant_id}/growth-records/{record_id}", response_model=APIResponse[None],
               summary="Hapus catatan pertumbuhan (`growth_records`)")
def delete_growth_record(plant_id: int, record_id: int, db: Session = Depends(get_db)):
    service.delete_growth_record(db, plant_id, record_id)
    return success_response(None, "Catatan pertumbuhan berhasil dihapus")


@router.get("/{plant_id}/growth-chart", response_model=APIResponse[GrowthChartOut],
            summary="Data time-series untuk Growth Chart (Chart.js / ApexCharts)")
def growth_chart(
    plant_id: int,
    label_mode: Literal["day", "date"] = Query("day", description="day = 'HST n', date = tanggal"),
    include_reference: bool = Query(True, description="Sertakan kurva tinggi ideal sebagai pembanding"),
    db: Session = Depends(get_db),
):
    chart = service.build_growth_chart(db, plant_id, label_mode, include_reference)
    return success_response(GrowthChartOut(**chart), "Data grafik pertumbuhan")
