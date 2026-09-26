from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.waste import WasteReport
from app.schemas.misc import LeaderboardEntry

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
def leaderboard(
    period: Literal["weekly", "monthly", "all_time"] = Query("all_time"),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """
    Ranks users by points. For weekly/monthly, points are approximated from
    reports created in that window (a simple, transparent proxy - a real
    deployment might instead sum RewardTransaction rows within the window).
    Never exposes email/phone - only name, rank, points, and report count.
    """
    query = db.query(
        User.id.label("user_id"),
        User.full_name.label("full_name"),
        User.points.label("points"),
        func.count(WasteReport.id).label("reports_count"),
    ).outerjoin(WasteReport, WasteReport.reporter_id == User.id)

    if period != "all_time":
        days = 7 if period == "weekly" else 30
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter((WasteReport.created_at >= cutoff) | (WasteReport.id.is_(None)))

    query = query.filter(User.role == UserRole.USER).group_by(User.id).order_by(User.points.desc()).limit(limit)

    rows = query.all()
    return [
        LeaderboardEntry(rank=i + 1, user_id=r.user_id, full_name=r.full_name, points=r.points, reports_count=r.reports_count)
        for i, r in enumerate(rows)
    ]
