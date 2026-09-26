"""
Thin service layer between FastAPI routes and the standalone `ml/` package.
Keeps ML logic out of route handlers per the project's architecture rules.
"""
import sys
from pathlib import Path

# ml/ lives one level up from backend/, as a sibling package.
_ML_ROOT = Path(__file__).resolve().parents[3]
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from app.core.config import settings  # noqa: E402

try:
    from ml.predict import classify_image as _classify_image  # noqa: E402
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "Could not import the ml package. Make sure ml/requirements.txt is installed "
        "and that the ml/ folder sits alongside backend/ in the project root."
    ) from exc


def classify_waste_image(image_bytes: bytes) -> dict:
    """Returns a dict: category, confidence, recyclable, recommended_disposal, mode, model_version."""
    result = _classify_image(image_bytes, mode=settings.ML_MODE)
    return result.to_dict()
