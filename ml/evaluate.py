"""
Evaluates the trained model on the held-out test set.
Produces accuracy, precision, recall, F1-score and a confusion matrix.

Usage:
    python ml/evaluate.py
"""
import json

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow import keras

from ml.config import BATCH_SIZE, IMAGE_SIZE, LABELS_PATH, MODEL_DIR, MODEL_PATH, TEST_DIR


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No trained model found at {MODEL_PATH}. Run `python ml/train.py` first."
        )

    model = keras.models.load_model(MODEL_PATH)
    with open(LABELS_PATH) as f:
        class_names = json.load(f)

    test_ds = keras.utils.image_dataset_from_directory(
        TEST_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE, label_mode="int", shuffle=False
    )

    y_true = np.concatenate([y.numpy() for _, y in test_ds])
    y_pred_probs = model.predict(test_ds)
    y_pred = np.argmax(y_pred_probs, axis=1)

    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    print(classification_report(y_true, y_pred, target_names=class_names))

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=class_names, yticklabels=class_names, cmap="Greens")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("EcoTrack Waste Classifier - Confusion Matrix")
    plt.tight_layout()
    plt.savefig(MODEL_DIR / "confusion_matrix.png")
    print(f"\nSaved confusion matrix to {MODEL_DIR / 'confusion_matrix.png'}")

    with open(MODEL_DIR / "evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved full classification report to {MODEL_DIR / 'evaluation_report.json'}")


if __name__ == "__main__":
    main()
