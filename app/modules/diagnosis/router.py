"""AI Diagnosis: Diagnosis Kesehatan Tanaman Selada (`diagnosis_records` + KB) - KARYAWAN (& OWNER)."""
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.enums import PlantPart
from app.common.responses import COMMON_ERROR_RESPONSES, APIResponse, pagination_meta, success_response
from app.core.database import get_db
from app.core.dependencies import require_karyawan
from app.modules.diagnosis import service
from app.modules.diagnosis.cv_detector import CLASS_LABELS, lettuce_detector
from app.modules.diagnosis.schemas import DiagnosisListItem, DiagnosisOut
from app.modules.employees.models import User
from app.modules.knowledge_base.models import DiseaseInfo, NutritionCondition
from app.modules.knowledge_base.schemas import DiseaseInfoOut, NutritionConditionOut

router = APIRouter(
    prefix="/diagnosis",
    tags=["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
    dependencies=[Depends(require_karyawan)],
    responses=COMMON_ERROR_RESPONSES,
)


@router.post("/predict", response_model=APIResponse[DiagnosisOut], status_code=status.HTTP_201_CREATED,
             summary="Upload foto selada & simpan diagnosis ke `diagnosis_records`")
async def predict(
    file: UploadFile = File(..., description="Foto tanaman selada (.jpg / .jpeg / .png, maks 5 MB)"),
    plant_id: int | None = Form(None, description="ID tanaman pada `plants` (jika kosong otomatis tanaman terbaru)"),
    plant_part: PlantPart = Form(PlantPart.daun, description="Bagian tanaman: daun | akar | seluruh_tanaman"),
    sumber_data: str | None = Form("upload_aplikasi", description="Asal gambar / dataset"),
    keterangan: str | None = Form(None, description="Catatan tambahan (opsional)"),
    notes: str | None = Form(None, description="Alias untuk `keterangan`"),
    db: Session = Depends(get_db),
    user: User = Depends(require_karyawan),
):
    record = await service.create_diagnosis(
        db, file, user,
        plant_id=plant_id,
        plant_part=plant_part,
        sumber_data=sumber_data,
        keterangan_tambahan=keterangan or notes,
    )
    return success_response(
        DiagnosisOut.model_validate(record),
        "Diagnosis berhasil dilakukan",
        {"model_mode": lettuce_detector.mode, "classes": CLASS_LABELS},
    )


@router.get("/history", response_model=APIResponse[list[DiagnosisListItem]],
            summary="Riwayat diagnosis (`diagnosis_records`)")
def history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    plant_id: int | None = Query(None),
    kelas_diagnosis: str | None = Query(None, alias="diagnosis_label",
                                        description=f"Filter: {', '.join(CLASS_LABELS)}"),
    mine_only: bool = Query(False, description="Hanya diagnosis yang saya buat"),
    db: Session = Depends(get_db),
    user: User = Depends(require_karyawan),
):
    items, total = service.list_diagnoses(
        db, page=page, per_page=per_page, plant_id=plant_id,
        kelas_diagnosis=kelas_diagnosis, mine_only=mine_only, user=user,
    )
    return success_response(
        [DiagnosisListItem.model_validate(d) for d in items],
        "Riwayat diagnosis berhasil diambil",
        pagination_meta(page, per_page, total, stats_by_label=service.diagnosis_stats(db)),
    )


@router.get("/diseases", response_model=APIResponse[list[DiseaseInfoOut]],
            summary="Basis pengetahuan penyakit (`disease_infos`)")
def list_diseases(db: Session = Depends(get_db)):
    rows = db.scalars(select(DiseaseInfo).order_by(DiseaseInfo.id)).all()
    return success_response([DiseaseInfoOut.model_validate(r) for r in rows], "Daftar informasi penyakit")


@router.get("/nutrition-conditions", response_model=APIResponse[list[NutritionConditionOut]],
            summary="Basis pengetahuan kondisi nutrisi (`nutrition_conditions`)")
def list_nutrition_conditions(db: Session = Depends(get_db)):
    rows = db.scalars(select(NutritionCondition).order_by(NutritionCondition.id)).all()
    return success_response([NutritionConditionOut.model_validate(r) for r in rows], "Daftar kondisi nutrisi")


@router.get("/{diagnosis_id}", response_model=APIResponse[DiagnosisOut], summary="Detail hasil diagnosis")
def detail(diagnosis_id: int, db: Session = Depends(get_db)):
    return success_response(DiagnosisOut.model_validate(service.get_diagnosis(db, diagnosis_id)), "Detail diagnosis")


@router.delete("/{diagnosis_id}", response_model=APIResponse[None], summary="Hapus hasil diagnosis")
def delete(diagnosis_id: int, db: Session = Depends(get_db), user: User = Depends(require_karyawan)):
    service.delete_diagnosis(db, diagnosis_id, user)
    return success_response(None, "Diagnosis berhasil dihapus")
