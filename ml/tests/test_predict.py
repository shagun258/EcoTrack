"""
ML tests that don't require TensorFlow or a trained model, so they run
in any environment. Run from the project root:

    python -m pytest ml/tests/ -q
"""
import io
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.config import CATEGORIES
from ml.predict import classify_image, predict_demo, predict_production


def _sample_image_bytes(color=(50, 160, 50)) -> bytes:
    img = Image.new("RGB", (150, 150), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_demo_prediction_returns_valid_category():
    result = predict_demo(_sample_image_bytes())
    assert result.category in CATEGORIES
    assert 0.0 <= result.confidence <= 1.0
    assert result.mode == "demo"


def test_demo_prediction_is_deterministic():
    """Same image in, same prediction out - it's a heuristic, not random."""
    data = _sample_image_bytes()
    r1 = predict_demo(data)
    r2 = predict_demo(data)
    assert r1.category == r2.category
    assert r1.confidence == r2.confidence


def test_classify_image_dispatches_to_demo_by_default():
    result = classify_image(_sample_image_bytes(), mode="demo")
    assert result.mode == "demo"


def test_production_mode_without_trained_model_raises_clear_error():
    """Guards against silently pretending a demo result is a real prediction."""
    with pytest.raises(FileNotFoundError, match="ML_MODE=production"):
        predict_production(_sample_image_bytes())


def test_prediction_result_serializes_expected_fields():
    result = predict_demo(_sample_image_bytes())
    data = result.to_dict()
    assert set(data.keys()) == {
        "category", "confidence", "recyclable", "recommended_disposal", "mode", "model_version",
    }
