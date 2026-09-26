from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.waste import ReportStatus, WasteCategory


class MLPredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    category: str = Field(validation_alias="predicted_category")
    confidence: float
    recyclable: bool
    recommended_disposal: str
    mode: str


class WasteReportCreate(BaseModel):
    description: str | None = None
    category: WasteCategory | None = None  # optional manual override
    latitude: float
    longitude: float
    address: str | None = None


class WasteReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter_id: int
    image_url: str
    description: str | None
    category: WasteCategory
    status: ReportStatus
    latitude: float
    longitude: float
    address: str | None
    possible_duplicate_of: int | None
    created_at: datetime
    ml_prediction: MLPredictionOut | None = None


class DuplicateCheckResult(BaseModel):
    possible_duplicate: bool
    similarity: float
    existing_report_id: int | None = None
