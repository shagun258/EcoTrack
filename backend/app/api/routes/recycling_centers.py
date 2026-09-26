import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.models.recycling_center import RecyclingCenter, RecyclingCenterWasteType
from app.schemas.recycling_center import (
    RecyclingCenterCreate,
    RecyclingCenterNearbyOut,
    RecyclingCenterOut,
    RecyclingCenterUpdate,
)

router = APIRouter(prefix="/api/recycling-centers", tags=["recycling-centers"])


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


@router.get("", response_model=list[RecyclingCenterOut])
def list_centers(waste_type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(RecyclingCenter).filter(RecyclingCenter.is_active.is_(True))
    if waste_type:
        query = query.join(RecyclingCenterWasteType).filter(RecyclingCenterWasteType.waste_type == waste_type)
    centers = query.all()
    return [RecyclingCenterOut.from_orm_with_types(c) for c in centers]


@router.get("/nearby", response_model=list[RecyclingCenterNearbyOut])
def nearby_centers(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius_km: float = Query(10.0, gt=0, le=100),
    waste_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(RecyclingCenter).filter(RecyclingCenter.is_active.is_(True))
    if waste_type:
        query = query.join(RecyclingCenterWasteType).filter(RecyclingCenterWasteType.waste_type == waste_type)

    results = []
    for center in query.all():
        distance = _haversine_km(latitude, longitude, center.latitude, center.longitude)
        if distance <= radius_km:
            out = RecyclingCenterNearbyOut.from_orm_with_types(center)
            out.distance_km = round(distance, 2)
            results.append(out)

    results.sort(key=lambda c: c.distance_km)
    return results


@router.get("/{center_id}", response_model=RecyclingCenterOut)
def get_center(center_id: int, db: Session = Depends(get_db)):
    center = db.get(RecyclingCenter, center_id)
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling center not found")
    return RecyclingCenterOut.from_orm_with_types(center)


@router.post("", response_model=RecyclingCenterOut, status_code=status.HTTP_201_CREATED)
def create_center(payload: RecyclingCenterCreate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    data = payload.model_dump(exclude={"accepted_waste_types"})
    center = RecyclingCenter(**data)
    db.add(center)
    db.flush()
    for wt in payload.accepted_waste_types:
        db.add(RecyclingCenterWasteType(center_id=center.id, waste_type=wt))
    db.commit()
    db.refresh(center)
    return RecyclingCenterOut.from_orm_with_types(center)


@router.patch("/{center_id}", response_model=RecyclingCenterOut)
def update_center(center_id: int, payload: RecyclingCenterUpdate, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    center = db.get(RecyclingCenter, center_id)
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling center not found")

    update_data = payload.model_dump(exclude_unset=True, exclude={"accepted_waste_types"})
    for field, value in update_data.items():
        setattr(center, field, value)

    if payload.accepted_waste_types is not None:
        db.query(RecyclingCenterWasteType).filter(RecyclingCenterWasteType.center_id == center.id).delete()
        for wt in payload.accepted_waste_types:
            db.add(RecyclingCenterWasteType(center_id=center.id, waste_type=wt))

    db.commit()
    db.refresh(center)
    return RecyclingCenterOut.from_orm_with_types(center)


@router.delete("/{center_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_center(center_id: int, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    center = db.get(RecyclingCenter, center_id)
    if not center:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recycling center not found")
    center.is_active = False
    db.commit()
    return None
