"""Shared configuration for the EcoTrack waste-classification model."""
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent

CATEGORIES = [
    "Plastic",
    "Paper",
    "Glass",
    "Metal",
    "Organic",
    "E-Waste",
    "Textile",
    "Other",
]

# Maps each category to whether it's generally recyclable and where it should go.
CATEGORY_META = {
    "Plastic":  {"recyclable": True,  "disposal": "Recycling Center"},
    "Paper":    {"recyclable": True,  "disposal": "Recycling Center"},
    "Glass":    {"recyclable": True,  "disposal": "Recycling Center"},
    "Metal":    {"recyclable": True,  "disposal": "Recycling Center"},
    "Organic":  {"recyclable": True,  "disposal": "Compost Facility"},
    "E-Waste":  {"recyclable": True,  "disposal": "E-Waste Collection Center"},
    "Textile":  {"recyclable": True,  "disposal": "Textile Donation/Recycling Bin"},
    "Other":    {"recyclable": False, "disposal": "General Waste"},
}

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
DATASET_DIR = ML_ROOT / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "val"
TEST_DIR = DATASET_DIR / "test"
MODEL_DIR = ML_ROOT / "models"
MODEL_PATH = MODEL_DIR / "waste_classifier.h5"
LABELS_PATH = MODEL_DIR / "labels.json"
