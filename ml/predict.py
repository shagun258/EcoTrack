"""
Inference entry point used by the FastAPI backend (via app/services/ml_service.py).

Two modes, controlled by ML_MODE in backend/.env:

  ML_MODE=production
      Loads the real trained Keras model from ml/models/waste_classifier.h5.
      Raises a clear error if the file is missing - it never silently
      falls back to demo mode, so you can't accidentally ship fake results.

  ML_MODE=demo   (default, works with zero setup)
      Uses a lightweight, deterministic, *non-random* heuristic classifier
      based on colour-histogram and texture features. It is a genuinely
      functioning classifier -- just far weaker than the trained CNN -- and
      every response it returns is explicitly tagged "mode": "demo" so the
      UI can show a "demo prediction" badge. It is NOT a trained neural
      network and should not be presented as one.

CLI usage (for quick manual testing):
    python ml/predict.py path/to/image.jpg
"""
import json
import sys
from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image

from ml.config import CATEGORIES, CATEGORY_META, IMAGE_SIZE, LABELS_PATH, MODEL_PATH


@dataclass
class PredictionResult:
    category: str
    confidence: float
    recyclable: bool
    recommended_disposal: str
    mode: str
    model_version: str = "v1"

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "confidence": round(self.confidence, 4),
            "recyclable": self.recyclable,
            "recommended_disposal": self.recommended_disposal,
            "mode": self.mode,
            "model_version": self.model_version,
        }


# ---------------------------------------------------------------------------
# Production inference (real trained model)
# ---------------------------------------------------------------------------
_production_model = None
_production_labels: list[str] | None = None


def _load_production_model():
    global _production_model, _production_labels
    if _production_model is not None:
        return _production_model, _production_labels

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ML_MODE=production but no trained model found at {MODEL_PATH}.\n"
            "Either train one (see ml/train.py) and place it there, or set "
            "ML_MODE=demo in your .env while you don't have a trained model."
        )

    from tensorflow import keras  # imported lazily so demo mode has no TF dependency at runtime

    _production_model = keras.models.load_model(MODEL_PATH)
    if LABELS_PATH.exists():
        with open(LABELS_PATH) as f:
            _production_labels = json.load(f)
    else:
        _production_labels = CATEGORIES
    return _production_model, _production_labels


def predict_production(image_bytes: bytes) -> PredictionResult:
    # Check for the trained model file (and raise a clear, actionable error
    # if it's missing) before importing TensorFlow, so this fails fast with
    # a helpful message even in environments where TensorFlow isn't installed.
    model, labels = _load_production_model()

    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

    img = Image.open(BytesIO(image_bytes)).convert("RGB").resize(IMAGE_SIZE)
    arr = np.array(img, dtype=np.float32)
    arr = preprocess_input(arr)
    arr = np.expand_dims(arr, axis=0)

    probs = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(probs))
    category = labels[idx]
    confidence = float(probs[idx])
    meta = CATEGORY_META.get(category, {"recyclable": False, "disposal": "General Waste"})

    return PredictionResult(
        category=category,
        confidence=confidence,
        recyclable=meta["recyclable"],
        recommended_disposal=meta["disposal"],
        mode="production",
    )


# ---------------------------------------------------------------------------
# Demo-mode inference: a real, deterministic heuristic - not a stub, not random
# ---------------------------------------------------------------------------
def _extract_features(image_bytes: bytes) -> dict:
    img = Image.open(BytesIO(image_bytes)).convert("RGB").resize((128, 128))
    arr = np.array(img, dtype=np.float32) / 255.0

    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    brightness = float(arr.mean())
    saturation = float(arr.max(axis=-1).mean() - arr.min(axis=-1).mean())
    greenness = float((g - (r + b) / 2).mean())
    grayscale = arr.mean(axis=-1)
    edges = np.abs(np.diff(grayscale, axis=0)).mean() + np.abs(np.diff(grayscale, axis=1)).mean()
    metallic_hint = float((arr.std(axis=-1) < 0.03).mean())  # low colour variance per-pixel = shiny/gray surfaces

    return {
        "brightness": brightness,
        "saturation": saturation,
        "greenness": greenness,
        "edge_density": float(edges),
        "metallic_hint": metallic_hint,
        "mean_r": float(r.mean()),
        "mean_g": float(g.mean()),
        "mean_b": float(b.mean()),
    }


def _score_categories(f: dict) -> dict[str, float]:
    """Rule-based scoring. Deliberately simple and explainable - this is a
    stand-in for the CNN, not an attempt to imitate one."""
    scores = {c: 0.1 for c in CATEGORIES}

    if f["greenness"] > 0.05 and f["saturation"] > 0.15:
        scores["Organic"] += 0.5
    if f["metallic_hint"] > 0.25 and f["saturation"] < 0.12:
        scores["Metal"] += 0.5
    if f["brightness"] > 0.75 and f["saturation"] < 0.1:
        scores["Glass"] += 0.4
    if f["edge_density"] > 0.09 and f["mean_b"] > f["mean_r"]:
        scores["Plastic"] += 0.35
    if f["brightness"] > 0.55 and f["saturation"] < 0.08 and f["edge_density"] < 0.05:
        scores["Paper"] += 0.35
    if f["metallic_hint"] > 0.35 and f["edge_density"] > 0.1:
        scores["E-Waste"] += 0.3
    if f["saturation"] > 0.2 and f["edge_density"] > 0.08:
        scores["Textile"] += 0.25

    scores["Other"] += 0.15  # small constant floor so "Other" can still win on truly ambiguous images

    total = sum(scores.values())
    return {k: v / total for k, v in scores.items()}


def predict_demo(image_bytes: bytes) -> PredictionResult:
    features = _extract_features(image_bytes)
    scores = _score_categories(features)
    category = max(scores, key=scores.get)
    confidence = scores[category]
    meta = CATEGORY_META.get(category, {"recyclable": False, "disposal": "General Waste"})

    return PredictionResult(
        category=category,
        confidence=confidence,
        recyclable=meta["recyclable"],
        recommended_disposal=meta["disposal"],
        mode="demo",
        model_version="heuristic-v1",
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def classify_image(image_bytes: bytes, mode: str = "demo") -> PredictionResult:
    if mode == "production":
        return predict_production(image_bytes)
    return predict_demo(image_bytes)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ml/predict.py path/to/image.jpg")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    result = classify_image(data, mode="demo")
    print(json.dumps(result.to_dict(), indent=2))
