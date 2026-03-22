from fastapi import APIRouter
from app.api.v1.routes import health, ocr, tts, pipeline

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(ocr.router, prefix="/ocr", tags=["OCR"])
api_router.include_router(tts.router, prefix="/tts", tags=["TTS"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])