# EcoTrack ML Module

Waste image classifier: Plastic, Paper, Glass, Metal, Organic, E-Waste, Textile, Other.

## Two modes

- **demo** (default): a real but lightweight colour/texture heuristic classifier in `predict.py`.
  Works instantly, needs no dataset or GPU, and every response is tagged `"mode": "demo"`.
- **production**: MobileNetV2 transfer-learning model you train yourself.

## Training your own model

1. Collect images into `ml/dataset/raw/<Category>/*.jpg` for each of the 8 categories
   (a good public starting point is the TrashNet or Kaggle "Garbage Classification" datasets).
2. `pip install -r ml/requirements.txt`
3. `python -m ml.preprocessing.dataset_prep` — splits raw images 70/15/15 into train/val/test.
4. `python ml/train.py` — trains and saves `ml/models/waste_classifier.h5` + `labels.json`.
5. `python ml/evaluate.py` — prints precision/recall/F1 and saves a confusion matrix image.
6. In `backend/.env`, set `ML_MODE=production`. Restart the backend. Done — no code changes needed.

## Manual test

```
python ml/predict.py path/to/some_image.jpg
```

## Files

- `config.py` — categories, paths, image size
- `preprocessing/dataset_prep.py` — raw → train/val/test split
- `preprocessing/model_builder.py` — MobileNetV2 transfer-learning architecture
- `train.py` — training loop, callbacks, saves model + history
- `evaluate.py` — test-set metrics + confusion matrix
- `predict.py` — inference used by the backend (`ml_service.py` imports `classify_image`)
