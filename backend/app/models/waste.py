import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class WasteCategory(str, enum.Enum):
    PLASTIC = "Plastic"
    PAPER = "Paper"
    GLASS = "Glass"
    METAL = "Metal"
    ORGANIC = "Organic"
    E_WASTE = "E-Waste"
    TEXTILE = "Textile"
    OTHER = "Other"


class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    RESOLVED = "RESOLVED"


class WasteReport(Base):
    __tablename__ = "waste_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[WasteCategory] = mapped_column(Enum(WasteCategory), nullable=False)
    manual_category_override: Mapped[bool] = mapped_column(default=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.PENDING)
    possible_duplicate_of: Mapped[int | None] = mapped_column(ForeignKey("waste_reports.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reporter = relationship("User", back_populates="waste_reports", foreign_keys=[reporter_id])
    ml_prediction = relationship("MLPrediction", back_populates="waste_report", uselist=False)


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    waste_report_id: Mapped[int] = mapped_column(ForeignKey("waste_reports.id", ondelete="CASCADE"), unique=True)
    predicted_category: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    recyclable: Mapped[bool] = mapped_column(default=True)
    recommended_disposal: Mapped[str] = mapped_column(String(255), default="Recycling Center")
    mode: Mapped[str] = mapped_column(String(20), default="demo")  # "demo" | "production"
    model_version: Mapped[str] = mapped_column(String(50), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    waste_report = relationship("WasteReport", back_populates="ml_prediction")
