from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, require_collector
from app.db.session import get_db
from app.models.pickup import PickupRequest, PickupStatus
from app.models.user import User, UserRole
from app.schemas.pickup import PickupAssign, PickupCreate, PickupOut, PickupStatusUpdate
from app.services import reward_service
from app.services.notification_service import notify_user

router = APIRouter(prefix="/api/pickups", tags=["pickups"])

# Valid forward transitions only - prevents e.g. jumping straight to COMPLETED
ALLOWED_TRANSITIONS = {
    PickupStatus.PENDING: {PickupStatus.ASSIGNED, PickupStatus.CANCELLED},
    PickupStatus.ASSIGNED: {PickupStatus.ACCEPTED, PickupStatus.CANCELLED},
    PickupStatus.ACCEPTED: {PickupStatus.PICKED_UP, PickupStatus.CANCELLED},
    PickupStatus.PICKED_UP: {PickupStatus.COMPLETED},
    PickupStatus.COMPLETED: set(),
    PickupStatus.CANCELLED: set(),
}


@router.post("", response_model=PickupOut, status_code=status.HTTP_201_CREATED)
def create_pickup(payload: PickupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pickup = PickupRequest(requester_id=current_user.id, **payload.model_dump())
    db.add(pickup)
    db.commit()
    db.refresh(pickup)
    return pickup


@router.get("/my", response_model=list[PickupOut])
def my_pickups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(PickupRequest)
        .filter(PickupRequest.requester_id == current_user.id)
        .order_by(PickupRequest.created_at.desc())
        .all()
    )


@router.get("/assigned", response_model=list[PickupOut])
def assigned_pickups(db: Session = Depends(get_db), collector: User = Depends(require_collector)):
    return (
        db.query(PickupRequest)
        .filter(PickupRequest.collector_id == collector.id)
        .order_by(PickupRequest.preferred_date.asc())
        .all()
    )


@router.get("/{pickup_id}", response_model=PickupOut)
def get_pickup(pickup_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pickup = db.get(PickupRequest, pickup_id)
    if not pickup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found")
    allowed = current_user.id in (pickup.requester_id, pickup.collector_id) or current_user.role == UserRole.ADMIN
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this pickup")
    return pickup


@router.patch("/{pickup_id}/assign", response_model=PickupOut)
def assign_collector(pickup_id: int, payload: PickupAssign, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    pickup = db.get(PickupRequest, pickup_id)
    if not pickup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found")

    collector = db.get(User, payload.collector_id)
    if not collector or collector.role != UserRole.COLLECTOR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="collector_id must belong to a COLLECTOR user")

    pickup.collector_id = collector.id
    pickup.status = PickupStatus.ASSIGNED
    db.commit()
    db.refresh(pickup)

    notify_user(db, pickup.requester_id, "Pickup assigned", f"A collector has been assigned to pickup #{pickup.id}.")
    notify_user(db, collector.id, "New pickup assigned", f"You've been assigned pickup #{pickup.id}.")
    db.commit()
    return pickup


@router.patch("/{pickup_id}/status", response_model=PickupOut)
def update_status(pickup_id: int, payload: PickupStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pickup = db.get(PickupRequest, pickup_id)
    if not pickup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup request not found")

    is_owner_or_admin = current_user.role == UserRole.ADMIN or current_user.id == pickup.requester_id
    is_assigned_collector = current_user.id == pickup.collector_id
    if not (is_owner_or_admin or is_assigned_collector):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this pickup")

    if payload.status not in ALLOWED_TRANSITIONS.get(pickup.status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition pickup from {pickup.status.value} to {payload.status.value}",
        )

    pickup.status = payload.status
    if payload.notes:
        pickup.notes = payload.notes

    if payload.status == PickupStatus.COMPLETED:
        reward_service.award_points(db, pickup.requester, "PICKUP_COMPLETED", "Pickup completed")

    db.commit()
    db.refresh(pickup)

    notify_user(db, pickup.requester_id, "Pickup status updated", f"Pickup #{pickup.id} is now {pickup.status.value}.")
    db.commit()
    return pickup
