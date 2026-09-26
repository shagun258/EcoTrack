# Machine Learning

See also `ml/README.md` for the hands-on quickstart.

## Two honest modes

EcoTrack ships with **no pretrained neural network weights bundled** (they'd be
tens of MB and require a dataset you don't have yet). Instead:

- **`ML_MODE=demo`** (default): `ml/predict.py::predict_demo()` runs a real,
  deterministic, explainable rule-based classifier over colour/texture features
  (brightness, saturation, "greenness", edge density, a "metallic" heuristic from
  per-pixel colour variance). It is not a neural network and is meaningfully less
  accurate than a trained CNN — but it is a genuine, functioning classifier, not a
  stub, and every response is tagged `"mode": "demo"` end-to-end so the UI shows a
  visible badge and nobody mistakes it for the real thing.
- **`ML_MODE=production`**: loads `ml/models/waste_classifier.h5`, a MobileNetV2
  transfer-learning model you train yourself with the provided scripts. If the
  file is missing, the API returns `503` with a clear message rather than
  silently falling back to demo mode.

## Training pipeline

```
ml/dataset/raw/<Category>/*.jpg      (you provide this)
        │  python -m ml.preprocessing.dataset_prep
        ▼
ml/dataset/{train,val,test}/<Category>/*.jpg
        │  python ml/train.py
        ▼
ml/models/waste_classifier.h5 + labels.json + training_history.json
        │  python ml/evaluate.py
        ▼
ml/models/confusion_matrix.png + evaluation_report.json
```

### Architecture

MobileNetV2 (ImageNet-pretrained) as a frozen/partially-fine-tuned backbone +
`GlobalAveragePooling2D` → `Dropout(0.3)` → `Dense(128, relu)` →
`Dropout(0.2)` → `Dense(8, softmax)`. See `ml/preprocessing/model_builder.py`.

### Data augmentation

Random horizontal flip, rotation (±15%), zoom (±15%), contrast (±10%) — applied
only to the training split, in `ml/train.py::build_augmentation()`.

### Metrics produced by `evaluate.py`

- Accuracy, precision, recall, F1-score per class (`classification_report`)
- Full confusion matrix, saved as an image
- Everything also saved as JSON for the admin dashboard or a report

## Swapping in your trained model

1. Train (above) so `ml/models/waste_classifier.h5` and `ml/models/labels.json` exist.
2. In `backend/.env`, set `ML_MODE=production`.
3. Restart the backend. No code changes required — `ml_service.py` reads
   `settings.ML_MODE` on every request.

## Where a public dataset can come from

Good starting points if you don't have your own images: the "TrashNet" dataset
and the Kaggle "Garbage Classification" dataset both roughly map onto these
eight categories (you'll need to relabel/regroup a little — neither maps 1:1,
which is expected for a real project).

## Duplicate-report detection (NLP)

`backend/app/services/duplicate_service.py` uses TF-IDF + cosine similarity
(scikit-learn) over report descriptions, scoped to reports of the same category
within ~1km and the last 30 days. Never auto-deletes anything — it only sets
`possible_duplicate_of` on the new report, and the frontend shows a "possible
duplicate" warning. Threshold is `ML_DUPLICATE_SIMILARITY_THRESHOLD` (default
0.82) in `.env`.
