"""Manajemen Akun Karyawan - OWNER ONLY."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.responses import COMMON_ERROR_RESPONSES, APIResponse, pagination_meta, success_response
from app.core.database import get_db
from app.core.dependencies import require_owner
from app.modules.employees import service
from app.modules.employees.models import User
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate, UserOut

router = APIRouter(
    prefix="/employees",
    tags=["B. Manajemen Karyawan (OWNER)"],
    dependencies=[Depends(require_owner)],
    responses=COMMON_ERROR_RESPONSES,
)


@router.post("", response_model=APIResponse[UserOut], status_code=status.HTTP_201_CREATED,
             summary="Tambah akun karyawan baru")
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    user = service.create_employee(db, payload)
    return success_response(UserOut.model_validate(user), "Akun karyawan berhasil dibuat")


@router.get("", response_model=APIResponse[list[UserOut]], summary="Daftar semua akun karyawan")
def list_employees(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, description="Cari nama / username"),
    role: UserRole | None = Query(UserRole.karyawan, description="Filter role (default: karyawan)"),
    db: Session = Depends(get_db),
):
    items, total = service.list_employees(db, page=page, per_page=per_page, search=search, role=role)
    return success_response(
        [UserOut.model_validate(u) for u in items],
        "Daftar karyawan berhasil diambil",
        pagination_meta(page, per_page, total),
    )


@router.get("/{employee_id}", response_model=APIResponse[UserOut], summary="Detail akun karyawan")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return success_response(UserOut.model_validate(service.get_employee(db, employee_id)), "Detail karyawan")


@router.put("/{employee_id}", response_model=APIResponse[UserOut],
            summary="Edit akun karyawan (nama, username, role, reset password)")
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    user = service.update_employee(db, employee_id, payload)
    return success_response(UserOut.model_validate(user), "Akun karyawan berhasil diperbarui")


@router.delete("/{employee_id}", response_model=APIResponse[None], summary="Hapus akun karyawan")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner),
):
    service.delete_employee(db, employee_id, current_user=current_user)
    return success_response(None, "Akun karyawan berhasil dihapus")
