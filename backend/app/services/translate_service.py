# backend/services/translate_service.py

import httpx
from app.models.schemas import TranslationResult
from app.core.config import get_settings

settings = get_settings()


class TranslateService:

    async def translate(
        self,
        text: str,
        source_language: str = "hi",
        target_language: str = "en",
    ) -> TranslationResult:

        if not text.strip():
            return TranslationResult(
                original_text=text,
                translated_text="",
                source_language=source_language,
                target_language=target_language,
                success=False,
                error="Empty input text",
            )

        try:
            async with httpx.AsyncClient(timeout=30) as client:

                response = await client.post(
                    f"{settings.sarvam_base_url}/v1/translate",
                    headers={
                        "api-subscription-key": settings.sarvam_api_key,
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": text,
                        "source_language_code": source_language,
                        "target_language_code": target_language,
                        "speaker_gender": "Female",
                        "mode": "formal",
                        "enable_preprocessing": True,
                    },
                )

                response.raise_for_status()

                data = response.json()

                # DEBUG: print real API response
                print("SARVAM TRANSLATE RESPONSE:", data)

                translated = ""

                if "translated_text" in data:
                    translated = data["translated_text"]

                elif "translations" in data and len(data["translations"]) > 0:
                    translated = data["translations"][0].get("translated_text", "")

                return TranslationResult(
                    original_text=text,
                    translated_text=translated,
                    source_language=source_language,
                    target_language=target_language,
                    success=bool(translated),
                )

        except Exception as e:
            return TranslationResult(
                original_text=text,
                translated_text="",
                source_language=source_language,
                target_language=target_language,
                success=False,
                error=str(e),
            )