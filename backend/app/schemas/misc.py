from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RewardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    points: int
    reason: str
    created_at: datetime


class BadgeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    points_required: int
    icon: str


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    full_name: str
    points: int
    reports_count: int


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime


class ComplaintCreate(BaseModel):
    subject: str
    description: str


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject: str
    description: str
    status: str
    created_at: datetime


class AnalyticsOverview(BaseModel):
    total_users: int
    total_waste_reports: int
    total_pickups: int
    pickup_completion_rate: float
    waste_by_category: dict[str, int]
    reports_last_30_days: dict[str, int]
