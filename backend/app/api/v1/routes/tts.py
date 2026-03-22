from fastapi import APIRouter
from pydantic import BaseModel
from app.services.tts_service import TTSService

router = APIRouter()
tts_service = TTSService()


class TTSRequest(BaseModel):
    text: str


@router.post("/speak")
async def speak(request: TTSRequest):
    result = await tts_service.synthesize(request.text)
    return result