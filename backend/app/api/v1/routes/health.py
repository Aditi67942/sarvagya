from fastapi import APIRouter
from app.core.config import get_settings

settings = get_settings()

router = APIRouter()


@router.get("/")
async def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,   # ✅ FIXED
        "env": "development",           # ✅ TEMP (since not in config)
        "version": "0.1.0",
    }