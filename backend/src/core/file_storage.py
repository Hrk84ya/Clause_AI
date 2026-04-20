import shutil
from pathlib import Path

import magic
from fastapi import HTTPException, UploadFile, status

from src.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
}

MAX_UPLOAD_SIZE = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes


async def validate_file(file: UploadFile) -> str:
    """
    Validate uploaded file by checking magic bytes for MIME type.
    Returns the detected MIME type.
    Raises 415 for unsupported types, 413 for oversized files.
    """
    # Read first 8192 bytes for magic byte detection
    header = await file.read(8192)
    await file.seek(0)  # Reset file position

    # Check file size
    # Read the full content to check size
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset again

    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.max_upload_size_mb}MB",
        )

    # Detect MIME type using magic bytes
    detected_mime = magic.from_buffer(header, mime=True)

    if detected_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {detected_mime}. Allowed: PDF, DOCX, TXT",
        )

    return detected_mime


async def save_upload(user_id: str, document_id: str, file: UploadFile) -> tuple[str, int]:
    """
    Save uploaded file to UPLOAD_DIR/{user_id}/{document_id}/original{ext}.
    Returns (file_path, file_size_bytes).
    """
    # Determine extension from MIME type
    header = await file.read(8192)
    await file.seek(0)
    detected_mime = magic.from_buffer(header, mime=True)
    ext = ALLOWED_MIME_TYPES.get(detected_mime, "")

    # Create directory
    upload_dir = Path(settings.upload_dir) / user_id / document_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = upload_dir / f"original{ext}"
    content = await file.read()
    file_path.write_bytes(content)

    return str(file_path), len(content)


def get_file_path(user_id: str, document_id: str) -> Path:
    """
    Get the path to a document's original file.
    Raises 404 if not found.
    """
    upload_dir = Path(settings.upload_dir) / user_id / document_id

    if not upload_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found",
        )

    # Find the original file (could be .pdf, .docx, or .txt)
    for ext in ALLOWED_MIME_TYPES.values():
        file_path = upload_dir / f"original{ext}"
        if file_path.exists():
            # Security: verify path doesn't escape upload directory
            resolved = file_path.resolve()
            base = Path(settings.upload_dir).resolve()
            if not resolved.is_relative_to(base):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied",
                )
            return file_path

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Document file not found",
    )


def delete_document_files(user_id: str, document_id: str) -> None:
    """Remove the document's directory and all files."""
    upload_dir = Path(settings.upload_dir) / user_id / document_id
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
