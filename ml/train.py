"""
Trains the EcoTrack waste classifier via transfer learning on MobileNetV2.

Prerequisites:
    1. Populate ml/dataset/raw/<Category>/*.jpg for each category
    2. Run: python -m ml.preprocessing.dataset_prep
    3. Run: python ml/train.py

Outputs:
    ml/models/waste_classifier.h5
    ml/models/labels.json
    ml/models/training_history.json
"""
import json

import tensorflow as tf
from tensorflow import keras

from ml.config import BATCH_SIZE, CATEGORIES, IMAGE_SIZE, LABELS_PATH, MODEL_DIR, MODEL_PATH, TRAIN_DIR, VAL_DIR
from ml.preprocessing.model_builder import build_model

EPOCHS = 20


def build_augmentation() -> keras.Sequential:
    return keras.Sequential(
        [
            keras.layers.RandomFlip("horizontal"),
            keras.layers.RandomRotation(0.15),
            keras.layers.RandomZoom(0.15),
            keras.layers.RandomContrast(0.1),
        ],
        name="augmentation",
    )


def load_datasets():
    train_ds = keras.utils.image_dataset_from_directory(
        TRAIN_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE, label_mode="int"
    )
    val_ds = keras.utils.image_dataset_from_directory(
        VAL_DIR, image_size=IMAGE_SIZE, batch_size=BATCH_SIZE, label_mode="int"
    )

    class_names = train_ds.class_names  # alphabetical order set by directory names
    augmentation = build_augmentation()

    train_ds = train_ds.map(lambda x, y: (augmentation(x, training=True), y))
    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(tf.data.AUTOTUNE)
    return train_ds, val_ds, class_names


def main():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    train_ds, val_ds, class_names = load_datasets()
    print(f"Classes found on disk: {class_names}")

    model = build_model(fine_tune_at=100)
    model.summary()

    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2),
        keras.callbacks.ModelCheckpoint(str(MODEL_PATH), monitor="val_accuracy", save_best_only=True),
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

    model.save(MODEL_PATH)
    with open(LABELS_PATH, "w") as f:
        json.dump(class_names, f, indent=2)
    with open(MODEL_DIR / "training_history.json", "w") as f:
        json.dump({k: [float(v) for v in vals] for k, vals in history.history.items()}, f, indent=2)

    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved label order to {LABELS_PATH}")
    print("Run `python ml/evaluate.py` next to check test-set performance.")


if __name__ == "__main__":
    main()
