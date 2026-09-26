from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User
from app.services import ml_service
from app.services.storage_service import validate_and_read_image

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.post("/classify")
async def classify_image(image: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
    Standalone classification endpoint - lets the frontend preview a
    prediction before the user commits to submitting a full waste report.
    Does not persist anything to the database.
    """
    image_bytes = await validate_and_read_image(image)
    try:
        return ml_service.classify_waste_image(image_bytes)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Waste classification failed")


@router.get("/status")
def ml_status():
    return {"mode": settings.ML_MODE, "model_path": settings.ML_MODEL_PATH}
