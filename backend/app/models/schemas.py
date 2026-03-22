from pydantic import BaseModel
from typing import Optional


class OCRResult(BaseModel):
    text: Optional[str] = None
    success: bool
    error: Optional[str] = None


class TranslationResult(BaseModel):
    translated_text: Optional[str] = None
    success: bool
    error: Optional[str] = None


class TTSResponse(BaseModel):
    provider: str
    audio_base64: str
    success: bool
    error: Optional[str] = None


class PipelineResult(BaseModel):
    ocr_text: str
    translated_text: str
    braille_text: str
    audio_base64: str
    success: bool