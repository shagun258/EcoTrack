from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.models.pickup import PickupStatus


class PickupCreate(BaseModel):
    waste_type: str
    quantity_kg: float = Field(gt=0)
    address: str
    latitude: float
    longitude: float
    preferred_date: date
    preferred_time: time
    notes: str | None = None


class PickupStatusUpdate(BaseModel):
    status: PickupStatus
    notes: str | None = None


class PickupAssign(BaseModel):
    collector_id: int


class PickupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_id: int
    collector_id: int | None
    waste_type: str
    quantity_kg: float
    address: str
    latitude: float
    longitude: float
    preferred_date: date
    preferred_time: time
    notes: str | None
    proof_image_url: str | None
    status: PickupStatus
    created_at: datetime
    updated_at: datetime
