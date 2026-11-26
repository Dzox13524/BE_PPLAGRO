"""Models `inventory_items` & `stock_movements` - sesuai ERD `hidroponik_selada`."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import InventoryType, StockMovementType
from app.core.database import Base, CreatedAtMixin, TimestampMixin, db_enum


class InventoryItem(TimestampMixin, Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nama_barang: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    jenis: Mapped[InventoryType] = mapped_column(db_enum(InventoryType, "inventory_type"), nullable=False, index=True)
    satuan: Mapped[str] = mapped_column(String(30), nullable=False)
    jumlah_stok: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, server_default="0", nullable=False)
    stok_minimum: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), default=0, server_default="0", nullable=True)
    keterangan: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator = relationship("User", foreign_keys=[created_by], lazy="joined")
    movements: Mapped[list["StockMovement"]] = relationship(
        back_populates="inventory_item",
        cascade="all, delete-orphan",
        order_by=lambda: [StockMovement.tanggal.desc(), StockMovement.id.desc()],
    )

    @property
    def created_by_nama(self) -> str | None:
        return self.creator.nama if self.creator else None


class StockMovement(CreatedAtMixin, Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inventory_item_id: Mapped[int] = mapped_column(
        ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recorded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    jenis_pergerakan: Mapped[StockMovementType] = mapped_column(
        db_enum(StockMovementType, "stock_movement_type"), nullable=False
    )
    jumlah: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tanggal: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    keterangan: Mapped[str | None] = mapped_column(Text, nullable=True)

    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="movements", lazy="joined")
    recorder = relationship("User", foreign_keys=[recorded_by], lazy="joined")

    @property
    def recorded_by_nama(self) -> str | None:
        return self.recorder.nama if self.recorder else None

    @property
    def nama_barang(self) -> str | None:
        return self.inventory_item.nama_barang if self.inventory_item else None

    @property
    def satuan(self) -> str | None:
        return self.inventory_item.satuan if self.inventory_item else None

    @property
    def jenis_barang(self) -> str | None:
        return self.inventory_item.jenis.value if self.inventory_item and self.inventory_item.jenis else None
