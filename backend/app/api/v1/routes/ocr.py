# backend/app/api/v1/routes/ocr.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ocr_service import (
    SarvamOCRService,
    GoogleVisionOCRService,
    GeminiOCRService
)

router = APIRouter()


# ===== REQUEST MODEL =====
class OCRRequest(BaseModel):
    image_base64: str
    provider: str = "sarvam"  # default


# ===== ROUTE =====
@router.post("/extract", tags=["OCR"])
async def extract_text(request: OCRRequest):
    try:
        provider = request.provider.lower()

        if provider == "sarvam":
            service = SarvamOCRService()

        elif provider == "google":
            service = GoogleVisionOCRService()

        elif provider == "gemini":
            service = GeminiOCRService()

        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        result = await service.extract_text(request.image_base64)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
