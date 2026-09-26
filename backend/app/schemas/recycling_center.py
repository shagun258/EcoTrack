from pydantic import BaseModel, ConfigDict


class RecyclingCenterCreate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str | None = None
    opening_hours: str | None = None
    accepted_waste_types: list[str] = []


class RecyclingCenterUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    phone: str | None = None
    opening_hours: str | None = None
    is_active: bool | None = None
    accepted_waste_types: list[str] | None = None


class RecyclingCenterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    phone: str | None
    opening_hours: str | None
    is_active: bool
    accepted_waste_types: list[str] = []

    @classmethod
    def from_orm_with_types(cls, center):
        data = cls.model_validate(center)
        data.accepted_waste_types = [t.waste_type for t in center.accepted_waste_types]
        return data


class RecyclingCenterNearbyOut(RecyclingCenterOut):
    distance_km: float
