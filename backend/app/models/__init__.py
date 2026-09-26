"""
Import every model here so Base.metadata is fully populated for Alembic
autogenerate and for `Base.metadata.create_all()` in dev/test setup.
"""
from app.models.user import User, UserRole  # noqa: F401
from app.models.waste import WasteReport, WasteCategory, ReportStatus, MLPrediction  # noqa: F401
from app.models.pickup import PickupRequest, PickupStatus  # noqa: F401
from app.models.recycling_center import RecyclingCenter, RecyclingCenterWasteType  # noqa: F401
from app.models.misc import (  # noqa: F401
    RewardTransaction,
    Badge,
    UserBadge,
    Notification,
    Complaint,
    ActivityLog,
)
