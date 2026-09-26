from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class RecyclingCenter(Base):
    __tablename__ = "recycling_centers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    accepted_waste_types = relationship(
        "RecyclingCenterWasteType", back_populates="center", cascade="all, delete-orphan"
    )


class RecyclingCenterWasteType(Base):
    __tablename__ = "recycling_center_waste_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    center_id: Mapped[int] = mapped_column(ForeignKey("recycling_centers.id", ondelete="CASCADE"), index=True)
    waste_type: Mapped[str] = mapped_column(String(50), nullable=False)

    center = relationship("RecyclingCenter", back_populates="accepted_waste_types")
