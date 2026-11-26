"""Business logic manajemen akun karyawan (role `owner` only)."""
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.exceptions import AppException, ConflictException, NotFoundException
from app.core.security import hash_password
from app.modules.employees.models import User
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate


def _ensure_unique_username(db: Session, username: str, exclude_id: int | None = None) -> None:
    stmt = select(User.id).where(func.lower(User.username) == username.lower())
    if exclude_id:
        stmt = stmt.where(User.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise ConflictException(f"Username '{username}' sudah digunakan.")


def list_employees(
    db: Session, *, page: int, per_page: int, search: str | None = None, role: UserRole | None = UserRole.karyawan
) -> tuple[list[User], int]:
    stmt = select(User)
    if role is not None:
        stmt = stmt.where(User.role == role)
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(or_(User.nama.ilike(like), User.username.ilike(like)))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.order_by(User.id.desc()).offset((page - 1) * per_page).limit(per_page)).all()
    return list(items), total


def get_employee(db: Session, employee_id: int) -> User:
    user = db.get(User, employee_id)
    if user is None:
        raise NotFoundException(f"Pengguna dengan id {employee_id} tidak ditemukan.")
    return user


def create_employee(db: Session, data: EmployeeCreate) -> User:
    username = data.username.strip().lower()
    _ensure_unique_username(db, username)

    user = User(
        nama=(data.nama or "").strip(),
        username=username,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_employee(db: Session, employee_id: int, data: EmployeeUpdate) -> User:
    user = get_employee(db, employee_id)
    payload = data.model_dump(exclude_unset=True)

    username = payload.get("username")
    if username:
        username = username.strip().lower()
        _ensure_unique_username(db, username, exclude_id=user.id)
        user.username = username

    if payload.get("nama") is not None:
        user.nama = payload["nama"].strip()
    if payload.get("role") is not None:
        user.role = payload["role"]
    if payload.get("password"):
        user.password = hash_password(payload["password"])

    db.commit()
    db.refresh(user)
    return user


def delete_employee(db: Session, employee_id: int, current_user: User | None = None) -> None:
    user = get_employee(db, employee_id)
    if current_user is not None and user.id == current_user.id:
        raise AppException("Tidak dapat menghapus akun yang sedang digunakan.", 400)

    if current_user is not None:
        from app.modules.diagnosis.models import DiagnosisRecord
        from app.modules.plants.models import GrowthRecord, Plant
        from app.modules.stocks.models import InventoryItem, StockMovement

        db.execute(update(Plant).where(Plant.created_by == user.id).values(created_by=current_user.id))
        db.execute(update(InventoryItem).where(InventoryItem.created_by == user.id).values(created_by=current_user.id))
        db.execute(update(StockMovement).where(StockMovement.recorded_by == user.id).values(recorded_by=current_user.id))
        db.execute(update(GrowthRecord).where(GrowthRecord.recorded_by == user.id).values(recorded_by=None))
        db.execute(update(DiagnosisRecord).where(DiagnosisRecord.diagnosed_by == user.id).values(diagnosed_by=None))

    db.delete(user)
    db.commit()
