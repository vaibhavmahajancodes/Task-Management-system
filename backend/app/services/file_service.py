import os
import re
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile, status

from app.config import settings

BASE_UPLOAD_DIR = Path(settings.UPLOAD_DIR).resolve()
BASE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(filename: str) -> str:
    name = os.path.basename(filename or "file")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:200] or "file"


def validate_upload(file: UploadFile) -> str:
    """Validates extension; returns the lowercased extension (with dot)."""
    original = file.filename or ""
    ext = Path(original).suffix.lower()
    if ext not in settings.allowed_upload_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed.",
        )
    return ext


async def save_upload(file: UploadFile, subfolder: str = "") -> Tuple[str, str, int, str]:
    """
    Streams the upload to disk in chunks (so large files don't blow up memory),
    enforcing the configured size limit as it goes.
    Returns (stored_file_name, relative_path, size_bytes, original_file_name).
    """
    ext = validate_upload(file)
    safe_original = _sanitize_filename(file.filename or "file")
    stored_name = f"{uuid.uuid4().hex}{ext}"

    target_dir = BASE_UPLOAD_DIR / subfolder if subfolder else BASE_UPLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / stored_name

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    size = 0
    chunk_size = 1024 * 1024

    with open(target_path, "wb") as out_file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            size += len(chunk)
            if size > max_bytes:
                out_file.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
                )
            out_file.write(chunk)

    relative_path = str((Path(subfolder) / stored_name)) if subfolder else stored_name
    return stored_name, relative_path, size, safe_original  # type: ignore[return-value]


def resolve_upload_path(relative_path: str) -> Path:
    """
    Safely resolves a stored relative path back to an absolute path,
    refusing to escape the upload directory (defends against path traversal).
    """
    candidate = (BASE_UPLOAD_DIR / relative_path).resolve()
    if BASE_UPLOAD_DIR not in candidate.parents and candidate != BASE_UPLOAD_DIR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file path.")
    if not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found.")
    return candidate
