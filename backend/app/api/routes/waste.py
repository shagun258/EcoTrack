from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.waste import MLPrediction, ReportStatus, WasteCategory, WasteReport
from app.schemas.waste import DuplicateCheckResult, WasteReportOut
from app.services import ml_service, reward_service
from app.services.duplicate_service import find_possible_duplicate
from app.services.storage_service import store_uploaded_image

router = APIRouter(prefix="/api/waste", tags=["waste"])


@router.post("/report", response_model=WasteReportOut, status_code=status.HTTP_201_CREATED)
async def create_waste_report(
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str | None = Form(None),
    address: str | None = Form(None),
    manual_category: WasteCategory | None = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_url, image_bytes = await store_uploaded_image(image, subfolder="waste_reports")

    try:
        prediction = ml_service.classify_waste_image(image_bytes)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Waste classification failed. Please try again.")

    final_category = manual_category or WasteCategory(prediction["category"])

    duplicate = find_possible_duplicate(db, description or "", final_category.value, latitude, longitude)

    report = WasteReport(
        reporter_id=current_user.id,
        image_url=image_url,
        description=description,
        category=final_category,
        manual_category_override=manual_category is not None,
        latitude=latitude,
        longitude=longitude,
        address=address,
        possible_duplicate_of=duplicate["existing_report_id"] if duplicate["possible_duplicate"] else None,
    )
    db.add(report)
    db.flush()

    db.add(
        MLPrediction(
            waste_report_id=report.id,
            predicted_category=prediction["category"],
            confidence=prediction["confidence"],
            recyclable=prediction["recyclable"],
            recommended_disposal=prediction["recommended_disposal"],
            mode=prediction["mode"],
            model_version=prediction["model_version"],
        )
    )

    reward_service.award_points(db, current_user, "WASTE_REPORTED", "Reported a waste item")

    db.commit()
    db.refresh(report)
    return report


@router.get("/reports", response_model=list[WasteReportOut])
def list_my_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(WasteReport)
        .filter(WasteReport.reporter_id == current_user.id)
        .order_by(WasteReport.created_at.desc())
        .all()
    )


@router.get("/reports/{report_id}", response_model=WasteReportOut)
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.get(WasteReport, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waste report not found")
    if report.reporter_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this report")
    return report


@router.patch("/reports/{report_id}/status", response_model=WasteReportOut)
def update_report_status(
    report_id: int,
    new_status: ReportStatus,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    report = db.get(WasteReport, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waste report not found")

    report.status = new_status
    if new_status == ReportStatus.VERIFIED:
        reward_service.award_points(db, report.reporter, "REPORT_VERIFIED", "Waste report verified by admin")

    db.commit()
    db.refresh(report)
    return report
