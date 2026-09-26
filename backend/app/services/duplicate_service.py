"""
Optional NLP component: flags possibly-duplicate waste reports by comparing
description text with TF-IDF + cosine similarity, scoped to reports near the
same location and category. Never auto-deletes anything - only flags.
"""
from datetime import datetime, timedelta, timezone

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.waste import WasteReport

NEARBY_DEGREES = 0.01  # ~1.1km at the equator; good enough for a campus/neighbourhood scale
LOOKBACK_DAYS = 30


def find_possible_duplicate(db: Session, description: str, category: str, latitude: float, longitude: float) -> dict:
    if not description or not description.strip():
        return {"possible_duplicate": False, "similarity": 0.0, "existing_report_id": None}

    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=LOOKBACK_DAYS)
    candidates = (
        db.query(WasteReport)
        .filter(
            WasteReport.category == category,
            WasteReport.created_at >= cutoff,
            WasteReport.latitude.between(latitude - NEARBY_DEGREES, latitude + NEARBY_DEGREES),
            WasteReport.longitude.between(longitude - NEARBY_DEGREES, longitude + NEARBY_DEGREES),
            WasteReport.description.isnot(None),
        )
        .all()
    )

    if not candidates:
        return {"possible_duplicate": False, "similarity": 0.0, "existing_report_id": None}

    corpus = [description] + [c.description for c in candidates]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

    best_idx = int(similarities.argmax())
    best_score = float(similarities[best_idx])

    if best_score >= settings.ML_DUPLICATE_SIMILARITY_THRESHOLD:
        return {
            "possible_duplicate": True,
            "similarity": round(best_score, 4),
            "existing_report_id": candidates[best_idx].id,
        }

    return {"possible_duplicate": False, "similarity": round(best_score, 4), "existing_report_id": None}
