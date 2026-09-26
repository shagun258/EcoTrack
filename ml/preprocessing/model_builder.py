"""Builds the transfer-learning model used for waste classification."""
from tensorflow import keras
from tensorflow.keras import layers

from ml.config import CATEGORIES, IMAGE_SIZE


def build_model(fine_tune_at: int | None = 100) -> keras.Model:
    """
    MobileNetV2 backbone (ImageNet weights) + a small classification head.

    fine_tune_at: if set, unfreezes backbone layers from this index onward
    so the later training epochs can fine-tune, not just train the head.
    Set to None to keep the whole backbone frozen (fastest, least data-hungry).
    """
    base_model = keras.applications.MobileNetV2(
        input_shape=IMAGE_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = fine_tune_at is not None
    if fine_tune_at is not None:
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False

    inputs = keras.Input(shape=IMAGE_SIZE + (3,))
    x = keras.applications.mobilenet_v2.preprocess_input(inputs)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(len(CATEGORIES), activation="softmax")(x)

    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
