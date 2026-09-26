"""
Storage abstraction so the rest of the app never cares whether an image
lives on local disk or in a cloud bucket.

Local mode requires zero external credentials and is the default.
"""
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

UPLOAD_ROOT = Path(settings.UPLOAD_DIR)
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)


def _safe_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    if ext not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image extension")
    return ext


async def validate_and_read_image(file: UploadFile) -> bytes:
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image type")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large ({size_mb:.1f}MB). Max is {settings.MAX_UPLOAD_SIZE_MB}MB.",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    return contents


def save_image_local(contents: bytes, original_filename: str, subfolder: str = "waste_reports") -> str:
    """Generates a random, safe filename (never trusts user input) and writes to disk.
    Returns a URL path the frontend can use, e.g. /uploads/waste_reports/<uuid>.jpg
    """
    ext = _safe_extension(original_filename)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    folder = UPLOAD_ROOT / subfolder
    folder.mkdir(parents=True, exist_ok=True)

    dest = folder / safe_name
    # Defensive: ensure the resolved path is still inside UPLOAD_ROOT (no path traversal)
    if UPLOAD_ROOT.resolve() not in dest.resolve().parents and dest.resolve() != UPLOAD_ROOT.resolve():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path")

    with open(dest, "wb") as f:
        f.write(contents)

    return f"/uploads/{subfolder}/{safe_name}"


def save_image_cloudinary(contents: bytes, original_filename: str) -> str:
    """Stub for Cloudinary upload. Requires CLOUDINARY_* env vars to be set.
    Raises clearly if credentials are missing rather than silently failing.
    """
    if not settings.CLOUDINARY_CLOUD_NAME:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STORAGE_PROVIDER=cloudinary but CLOUDINARY_* credentials are not configured",
        )
    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )
    result = cloudinary.uploader.upload(contents, folder="ecotrack/waste_reports")
    return result["secure_url"]


async def store_uploaded_image(file: UploadFile, subfolder: str = "waste_reports") -> tuple[str, bytes]:
    """Validates, then stores according to STORAGE_PROVIDER. Returns (url, raw_bytes)."""
    contents = await validate_and_read_image(file)
    if settings.STORAGE_PROVIDER == "cloudinary":
        url = save_image_cloudinary(contents, file.filename or "upload.jpg")
    else:
        url = save_image_local(contents, file.filename or "upload.jpg", subfolder)
    return url, contents
