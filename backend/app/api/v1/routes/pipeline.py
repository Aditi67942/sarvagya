import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.schemas import PipelineResult
from app.services.ocr_service import (
    SarvamOCRService,
    GoogleVisionOCRService,
    GeminiOCRService,
)
from app.services.consensus_engine import ConsensusEngine
from app.services.translate_service import TranslateService
from app.services.braille_service import BrailleService
from app.services.tts_service import TTSService
from app.utils.file_utils import validate_upload, read_file_as_base64

router = APIRouter()

# Services
sarvam_ocr = SarvamOCRService()
google_ocr = GoogleVisionOCRService()
gemini_ocr = GeminiOCRService()

consensus = ConsensusEngine()
translator = TranslateService()
braille_svc = BrailleService()
tts_svc = TTSService()


@router.get("/status")
async def status():
    return {"message": "Pipeline is alive"}


@router.post("/", response_model=PipelineResult)
async def run_pipeline(file: UploadFile = File(...)):
    validate_upload(file)

    image_base64 = await read_file_as_base64(file)

    # STEP 1 — OCR
    ocr_results = await asyncio.gather(
        sarvam_ocr.extract_text(image_base64),
        google_ocr.extract_text(image_base64),
        gemini_ocr.extract_text(image_base64),
    )

    consensus_result = consensus.resolve(list(ocr_results))

    if not consensus_result.final_text:
        raise HTTPException(status_code=422, detail="OCR failed")

    ocr_text = consensus_result.final_text.strip()

    # STEP 2 — Translation
    translation_result = await translator.translate(
        text=ocr_text,
        source_language="hi",
        target_language="en",
    )

    translated_text = translation_result.translated_text or ocr_text
    translated_text = translated_text.strip()

    # STEP 3 — Braille + TTS
    braille_result, tts_result = await asyncio.gather(
        asyncio.to_thread(braille_svc.translate, translated_text),
        tts_svc.synthesize(translated_text),
    )

    braille_text = braille_result.get("braille_text", "")

    return PipelineResult(
        ocr_text=ocr_text,
        translated_text=translated_text,
        braille_text=braille_text,
        audio_base64=tts_result["audio_base64"],
        success=True,
    )