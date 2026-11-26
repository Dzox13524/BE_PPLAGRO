"""Business logic AI 2 - upload gambar, jalankan model CV, petakan ke `disease_infos` &
`nutrition_conditions`, lalu simpan ke `diagnosis_records` (sesuai ERD `hidroponik_selada`)."""
import logging
from decimal import Decimal

from fastapi import UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.enums import PlantPart, UserRole
from app.common.exceptions import AppException, NotFoundException
from app.common.time import utcnow
from app.modules.diagnosis.cv_detector import lettuce_detector
from app.modules.diagnosis.models import DiagnosisRecord
from app.modules.employees.models import User
from app.modules.knowledge_base.models import DiseaseInfo, NutritionCondition
from app.modules.plants import service as plant_service
from app.modules.plants.models import Plant
from app.utils.file_handler import delete_file, save_upload_image

logger = logging.getLogger(__name__)


def _resolve_plant_id(db: Session, plant_id: int | None) -> int:
    """Kolom `diagnosis_records.plant_id` adalah NOT NULL di ERD.
    Jika `plant_id` tidak dikirim dari form, gunakan tanaman terbaru yang ada."""
    if plant_id is not None:
        plant_service.get_plant(db, plant_id)
        return plant_id
    first_id = db.scalar(select(Plant.id).order_by(Plant.id.desc()))
    if first_id is None:
        raise AppException(
            "plant_id wajib diisi (belum ada data tanaman pada tabel `plants`).",
            status.HTTP_400_BAD_REQUEST,
        )
    return first_id


def _match_disease_info(db: Session, label: str) -> DiseaseInfo | None:
    clean_label = label.replace("_", " ").strip()
    match = db.scalar(select(DiseaseInfo).where(DiseaseInfo.nama_penyakit.ilike(f"%{clean_label}%")))
    if not match:
        for word in clean_label.split():
            if len(word) > 3:
                match = db.scalar(select(DiseaseInfo).where(DiseaseInfo.nama_penyakit.ilike(f"%{word}%")))
                if match:
                    break
    return match


def _match_nutrition_condition(db: Session, label: str, nutrient_text: str) -> NutritionCondition | None:
    text = nutrient_text.lower()
    if label == "Tip Burn" or "kalsium" in text:
        key = "Kalsium"
    elif "kekurangan nitrogen" in text:
        key = "Kekurangan Nitrogen"
    elif "kelebihan nitrogen" in text:
        key = "Kelebihan Nitrogen"
    elif "kalium" in text:
        key = "Kalium"
    else:
        key = "Normal"
    return db.scalar(select(NutritionCondition).where(NutritionCondition.nama_kondisi.ilike(f"%{key}%")))


async def create_diagnosis(
    db: Session,
    file: UploadFile,
    user: User,
    *,
    plant_id: int | None = None,
    plant_part: PlantPart = PlantPart.daun,
    sumber_data: str | None = "upload_aplikasi",
    keterangan_tambahan: str | None = None,
) -> DiagnosisRecord:
    resolved_plant_id = _resolve_plant_id(db, plant_id)

    saved = await save_upload_image(file, subdir="diagnosis")
    try:
        result = await run_in_threadpool(lettuce_detector.predict, saved.content)
    except Exception as exc:
        logger.exception("Diagnosis gagal: %s", exc)
        delete_file(saved.relative_path)
        raise AppException("Gagal memproses gambar untuk diagnosis.", status.HTTP_422_UNPROCESSABLE_ENTITY)

    disease_row = _match_disease_info(db, result.diagnosis_label)
    nutrition_row = _match_nutrition_condition(db, result.diagnosis_label, result.nutrient_condition)

    ket = result.plant_condition_summary
    if keterangan_tambahan:
        ket = f"{keterangan_tambahan} | {ket}"
    rekom = " ".join(f"{i}) {t}" for i, t in enumerate(result.treatment_recommendations, 1))

    record = DiagnosisRecord(
        plant_id=resolved_plant_id,
        diagnosed_by=user.id,
        tanggal_diagnosis=utcnow(),
        image_path=saved.relative_path,
        plant_part=plant_part,
        kelas_diagnosis=result.diagnosis_label,
        confidence=Decimal(f"{result.confidence:.5f}"),
        disease_info_id=disease_row.id if disease_row else None,
        nutrition_condition_id=nutrition_row.id if nutrition_row else None,
        model=(result.model_source or "YOLO")[:50],
        versi_model=result.model_version[:50],
        sumber_data=sumber_data,
        keterangan=ket,
        rekomendasi=rekom,
    )
    try:
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()
        delete_file(saved.relative_path)
        raise
    db.refresh(record)
    return record


def list_diagnoses(
    db: Session, *, page: int, per_page: int, plant_id: int | None = None,
    kelas_diagnosis: str | None = None, mine_only: bool = False, user: User | None = None,
) -> tuple[list[DiagnosisRecord], int]:
    stmt = select(DiagnosisRecord)
    if plant_id is not None:
        stmt = stmt.where(DiagnosisRecord.plant_id == plant_id)
    if kelas_diagnosis:
        stmt = stmt.where(DiagnosisRecord.kelas_diagnosis == kelas_diagnosis)
    if mine_only and user is not None:
        stmt = stmt.where(DiagnosisRecord.diagnosed_by == user.id)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(DiagnosisRecord.tanggal_diagnosis.desc(), DiagnosisRecord.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).unique().all()
    return list(items), total


def diagnosis_stats(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(DiagnosisRecord.kelas_diagnosis, func.count(DiagnosisRecord.id))
        .group_by(DiagnosisRecord.kelas_diagnosis)
    )
    return {label: count for label, count in rows}


def get_diagnosis(db: Session, diagnosis_id: int) -> DiagnosisRecord:
    record = db.get(DiagnosisRecord, diagnosis_id)
    if record is None:
        raise NotFoundException(f"Diagnosis dengan id {diagnosis_id} tidak ditemukan.")
    return record


def delete_diagnosis(db: Session, diagnosis_id: int, user: User) -> None:
    record = get_diagnosis(db, diagnosis_id)
    if user.role != UserRole.owner and record.diagnosed_by != user.id:
        raise AppException("Anda hanya dapat menghapus diagnosis milik sendiri.", status.HTTP_403_FORBIDDEN)
    path = record.image_path
    db.delete(record)
    db.commit()
    delete_file(path)
