# backend/utils/file_utils.py
"""
File utilities for upload handling and validation.

Handles:
- File type validation
- Size validation
- Base64 encoding for API transmission
- File persistence
"""

import base64
import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings

settings = get_settings()


def validate_upload(file: UploadFile) -> None:
    """
    Validate uploaded file type and size.

    Args:
        file: Uploaded file from FastAPI

    Raises:
        HTTPException: If file type or size is invalid
    """
    ext = Path(file.filename).suffix.lower().strip(".")
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type '.{ext}' not allowed. Allowed: {settings.allowed_extensions_list}"
        )


async def read_file_as_base64(file: UploadFile) -> str:
    """
    Read uploaded file and convert to base64.

    Used for passing images to OCR APIs.

    Args:
        file: Uploaded file

    Returns:
        Base64-encoded file contents

    Raises:
        HTTPException: If file is too large
    """
    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB"
        )
    return base64.b64encode(contents).decode("utf-8")


async def save_upload(file: UploadFile) -> str:
    """
    Save uploaded file to disk.

    Args:
        file: Uploaded file

    Returns:
        Path to saved file
    """
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    return file_path
