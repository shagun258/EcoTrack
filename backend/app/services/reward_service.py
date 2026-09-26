"""
Reward-point rules, kept in one place so they're easy to tune.
Every award is written to `rewards` as an auditable transaction, and the
denormalised `users.points` total is updated alongside it.
"""
from sqlalchemy.orm import Session

from app.models.misc import Badge, RewardTransaction, UserBadge
from app.models.user import User

# Configurable point values
POINTS = {
    "WASTE_REPORTED": 10,
    "REPORT_VERIFIED": 15,
    "PICKUP_COMPLETED": 25,
    "RECYCLING_VERIFIED": 20,
    "CAMPAIGN_PARTICIPATION": 30,
}


def award_points(db: Session, user: User, reason_key: str, custom_reason: str | None = None) -> RewardTransaction:
    points = POINTS.get(reason_key, 0)
    tx = RewardTransaction(user_id=user.id, points=points, reason=custom_reason or reason_key)
    db.add(tx)
    user.points += points
    db.add(user)
    db.flush()

    _check_and_award_badges(db, user)
    return tx


def _check_and_award_badges(db: Session, user: User) -> None:
    earned_badge_ids = {ub.badge_id for ub in user.badges}
    eligible_badges = db.query(Badge).filter(Badge.points_required <= user.points).all()

    for badge in eligible_badges:
        if badge.id not in earned_badge_ids:
            db.add(UserBadge(user_id=user.id, badge_id=badge.id))
