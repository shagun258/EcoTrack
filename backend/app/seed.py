"""
Seeds the database with development sample data: an admin, a collector,
a few citizens, recycling centers, badges, waste reports and pickups.

Usage (from backend/):
    python -m app.seed

WARNING: development-only credentials below. Never reuse in production.
"""
import sys
from datetime import date, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.misc import Badge, RewardTransaction
from app.models.pickup import PickupRequest, PickupStatus
from app.models.recycling_center import RecyclingCenter, RecyclingCenterWasteType
from app.models.user import User, UserRole
from app.models.waste import MLPrediction, ReportStatus, WasteCategory, WasteReport

DEV_PASSWORD = "EcoTrack@123"  # noqa: S105 - intentional, development-only


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(User).count() > 0:
            print("Database already has users - skipping seed. Delete the DB and migrate again to reseed.")
            return

        admin = User(full_name="Admin User", email="admin@example.com", hashed_password=hash_password(DEV_PASSWORD), role=UserRole.ADMIN)
        collector = User(full_name="Collector Dev", email="collector@example.com", hashed_password=hash_password(DEV_PASSWORD), role=UserRole.COLLECTOR)
        citizen1 = User(full_name="Asha Sharma", email="asha@example.com", hashed_password=hash_password(DEV_PASSWORD), role=UserRole.USER, points=40)
        citizen2 = User(full_name="Rohan Verma", email="rohan@example.com", hashed_password=hash_password(DEV_PASSWORD), role=UserRole.USER, points=15)
        db.add_all([admin, collector, citizen1, citizen2])
        db.flush()

        badges = [
            Badge(name="Eco Beginner", description="Reported your first waste item", points_required=0, icon="seedling"),
            Badge(name="Plastic Reducer", description="Reached 25 points", points_required=25, icon="recycle"),
            Badge(name="Recycling Champion", description="Reached 100 points", points_required=100, icon="trophy"),
            Badge(name="Green Citizen", description="Reached 250 points", points_required=250, icon="leaf"),
        ]
        db.add_all(badges)
        db.flush()

        center1 = RecyclingCenter(
            name="Shimla Green Recycling Hub",
            address="Mall Road, Shimla, HP",
            latitude=31.1048, longitude=77.1734,
            phone="+91-90000-00001",
            opening_hours="Mon-Sat 9:00-18:00",
        )
        center2 = RecyclingCenter(
            name="Summer Hill E-Waste Center",
            address="Summer Hill, Shimla, HP",
            latitude=31.1120, longitude=77.1550,
            phone="+91-90000-00002",
            opening_hours="Mon-Fri 10:00-17:00",
        )
        db.add_all([center1, center2])
        db.flush()

        db.add_all([
            RecyclingCenterWasteType(center_id=center1.id, waste_type="Plastic"),
            RecyclingCenterWasteType(center_id=center1.id, waste_type="Paper"),
            RecyclingCenterWasteType(center_id=center1.id, waste_type="Glass"),
            RecyclingCenterWasteType(center_id=center1.id, waste_type="Metal"),
            RecyclingCenterWasteType(center_id=center2.id, waste_type="E-Waste"),
            RecyclingCenterWasteType(center_id=center2.id, waste_type="Metal"),
        ])

        report1 = WasteReport(
            reporter_id=citizen1.id,
            image_url="/uploads/waste_reports/sample-plastic.jpg",
            description="Garbage dumped near the college gate.",
            category=WasteCategory.PLASTIC,
            latitude=31.1050, longitude=77.1730,
            address="Near College Gate, Shimla",
            status=ReportStatus.VERIFIED,
        )
        db.add(report1)
        db.flush()
        db.add(MLPrediction(waste_report_id=report1.id, predicted_category="Plastic", confidence=0.94, recyclable=True, recommended_disposal="Recycling Center", mode="demo"))

        db.add(PickupRequest(
            requester_id=citizen1.id, collector_id=collector.id,
            waste_type="Plastic", quantity_kg=8.5, address="Near College Gate, Shimla",
            latitude=31.1050, longitude=77.1730,
            preferred_date=date(2026, 10, 2), preferred_time=time(10, 0),
            status=PickupStatus.ASSIGNED,
        ))
        db.add(PickupRequest(
            requester_id=citizen2.id,
            waste_type="E-Waste", quantity_kg=3.0, address="Summer Hill, Shimla",
            latitude=31.1120, longitude=77.1550,
            preferred_date=date(2026, 10, 5), preferred_time=time(14, 30),
            status=PickupStatus.PENDING,
        ))

        db.add(RewardTransaction(user_id=citizen1.id, points=40, reason="Seed data starting balance"))
        db.add(RewardTransaction(user_id=citizen2.id, points=15, reason="Seed data starting balance"))

        db.commit()
        print("Seed complete.\n")
        print("Development login credentials (all use the same password):")
        print(f"  Admin:     admin@example.com     / {DEV_PASSWORD}")
        print(f"  Collector: collector@example.com / {DEV_PASSWORD}")
        print(f"  Citizen:   asha@example.com       / {DEV_PASSWORD}")
        print(f"  Citizen:   rohan@example.com       / {DEV_PASSWORD}")
        print("\nThese are development-only credentials. Do not use in production.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
