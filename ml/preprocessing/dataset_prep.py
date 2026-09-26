"""
Dataset preparation for the EcoTrack waste classifier.

Expected raw layout before running this script (one folder per category,
images inside, any size/format):

    ml/dataset/raw/
        Plastic/*.jpg
        Paper/*.jpg
        Glass/*.jpg
        Metal/*.jpg
        Organic/*.jpg
        E-Waste/*.jpg
        Textile/*.jpg
        Other/*.jpg

This script splits each category 70/15/15 into train/val/test and copies
(not moves) the files into ml/dataset/{train,val,test}/<category>/, which is
the layout `train.py` expects via `keras.utils.image_dataset_from_directory`.

Usage:
    python -m ml.preprocessing.dataset_prep
"""
import random
import shutil
from pathlib import Path

from ml.config import CATEGORIES, DATASET_DIR, TEST_DIR, TRAIN_DIR, VAL_DIR

RAW_DIR = DATASET_DIR / "raw"
SPLIT_RATIOS = (0.70, 0.15, 0.15)  # train, val, test
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _list_images(folder: Path) -> list[Path]:
    return [p for p in folder.iterdir() if p.suffix.lower() in VALID_EXTENSIONS]


def split_dataset(seed: int = 42) -> None:
    random.seed(seed)

    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Expected raw dataset at {RAW_DIR}. Create one subfolder per category "
            f"({', '.join(CATEGORIES)}) containing images, then re-run this script."
        )

    for split_dir in (TRAIN_DIR, VAL_DIR, TEST_DIR):
        split_dir.mkdir(parents=True, exist_ok=True)

    summary = {}
    for category in CATEGORIES:
        src = RAW_DIR / category
        if not src.exists():
            print(f"[warn] no raw folder for category '{category}', skipping")
            continue

        images = _list_images(src)
        random.shuffle(images)

        n = len(images)
        n_train = int(n * SPLIT_RATIOS[0])
        n_val = int(n * SPLIT_RATIOS[1])

        splits = {
            "train": images[:n_train],
            "val": images[n_train : n_train + n_val],
            "test": images[n_train + n_val :],
        }

        for split_name, files in splits.items():
            dest_dir = DATASET_DIR / split_name / category
            dest_dir.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(f, dest_dir / f.name)

        summary[category] = {k: len(v) for k, v in splits.items()}
        print(f"{category}: {summary[category]}")

    print("\nDataset split complete.")
    print(summary)


if __name__ == "__main__":
    split_dataset()
