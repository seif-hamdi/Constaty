"""Local file storage service for uploaded evidence."""
from __future__ import annotations
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.config import settings

STORAGE_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "storage"


def claim_storage_dir(claim_id: str) -> Path:
    d = STORAGE_ROOT / "claims" / claim_id
    d.mkdir(parents=True, exist_ok=True)
    return d


async def save_upload(claim_id: str, file: UploadFile, prefix: str = "evidence") -> dict:
    """Save an uploaded file and return metadata."""
    d = claim_storage_dir(claim_id)
    ext = Path(file.filename or "").suffix or ".bin"
    file_id = f"{prefix}_{uuid.uuid4().hex[:8]}{ext}"
    path = d / file_id

    content = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise ValueError(f"File exceeds {settings.max_upload_mb}MB limit")

    path.write_bytes(content)

    return {
        "id": file_id.replace(ext, ""),
        "filename": file_id,
        "path": str(path),
        "url": f"/storage/claims/{claim_id}/{file_id}",
        "mime_type": file.content_type or "application/octet-stream",
        "size": len(content),
    }