from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.models.pickup import PickupRequest, PickupStatus
from app.models.user import User
from app.models.waste import WasteReport
from app.schemas.misc import AnalyticsOverview

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def overview(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_reports = db.query(func.count(WasteReport.id)).scalar() or 0
    total_pickups = db.query(func.count(PickupRequest.id)).scalar() or 0
    completed_pickups = db.query(func.count(PickupRequest.id)).filter(PickupRequest.status == PickupStatus.COMPLETED).scalar() or 0
    completion_rate = round((completed_pickups / total_pickups) * 100, 1) if total_pickups else 0.0

    waste_by_category = dict(
        db.query(WasteReport.category, func.count(WasteReport.id)).group_by(WasteReport.category).all()
    )
    waste_by_category = {k.value if hasattr(k, "value") else k: v for k, v in waste_by_category.items()}

    cutoff = datetime.utcnow() - timedelta(days=30)
    rows = (
        db.query(func.date(WasteReport.created_at), func.count(WasteReport.id))
        .filter(WasteReport.created_at >= cutoff)
        .group_by(func.date(WasteReport.created_at))
        .all()
    )
    reports_last_30_days = {str(day): count for day, count in rows}

    return AnalyticsOverview(
        total_users=total_users,
        total_waste_reports=total_reports,
        total_pickups=total_pickups,
        pickup_completion_rate=completion_rate,
        waste_by_category=waste_by_category,
        reports_last_30_days=reports_last_30_days,
    )
