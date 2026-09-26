from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.misc import Badge, RewardTransaction, UserBadge
from app.models.user import User
from app.models.waste import WasteReport
from app.schemas.misc import BadgeOut, RewardOut

router = APIRouter(prefix="/api/rewards", tags=["rewards"])


@router.get("/my", response_model=list[RewardOut])
def my_rewards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(RewardTransaction)
        .filter(RewardTransaction.user_id == current_user.id)
        .order_by(RewardTransaction.created_at.desc())
        .all()
    )


@router.get("/my/badges", response_model=list[BadgeOut])
def my_badges(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Badge)
        .join(UserBadge, UserBadge.badge_id == Badge.id)
        .filter(UserBadge.user_id == current_user.id)
        .all()
    )


@router.get("/badges", response_model=list[BadgeOut])
def all_badges(db: Session = Depends(get_db)):
    return db.query(Badge).order_by(Badge.points_required.asc()).all()
