# backend/app/services/ocr_service.py

import httpx
import base64
import json
import tempfile
import os
import asyncio
from abc import ABC, abstractmethod

from app.models.schemas import OCRResult
from app.core.config import get_settings

settings = get_settings()


class BaseOCRService(ABC):
    @abstractmethod
    async def extract_text(self, image_base64: str) -> OCRResult:
        pass


# ===================== SARVAM OCR =====================
class SarvamOCRService(BaseOCRService):
    async def extract_text(self, image_base64: str) -> OCRResult:
        try:
            if not settings.SARVAM_API_KEY:
                raise Exception("SARVAM_API_KEY not set")

            from sarvamai import SarvamAI
            import zipfile

            def run_sarvam_ocr():
                client = SarvamAI(api_subscription_key=settings.SARVAM_API_KEY)

                image_bytes = base64.b64decode(image_base64)

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    tmp.write(image_bytes)
                    tmp_path = tmp.name

                zip_path = None

                try:
                    job = client.document_intelligence.create_job(
                        language="hi-IN",
                        output_format="md"
                    )

                    job.upload_file(tmp_path)
                    job.start()
                    job.wait_until_complete()

                    zip_path = tmp_path + "_output.zip"
                    job.download_output(zip_path)

                    text = ""
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        for name in z.namelist():
                            with z.open(name) as f:
                                text += f.read().decode("utf-8", errors="ignore")

                    return text.strip()

                finally:
                    os.unlink(tmp_path)
                    if zip_path and os.path.exists(zip_path):
                        os.unlink(zip_path)

            text = await asyncio.to_thread(run_sarvam_ocr)

            return OCRResult(
                provider="sarvam",
                text=text,
                confidence=0.95,
                success=True,
            )

        except Exception as e:
            return OCRResult(
                provider="sarvam",
                text="",
                success=False,
                error=str(e),
            )


# ===================== GOOGLE VISION OCR =====================
class GoogleVisionOCRService(BaseOCRService):
    async def extract_text(self, image_base64: str) -> OCRResult:
        try:
            token = await self._get_access_token()

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    "https://vision.googleapis.com/v1/images:annotate",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "requests": [{
                            "image": {"content": image_base64},
                            "features": [{"type": "TEXT_DETECTION"}],
                        }]
                    },
                )

                response.raise_for_status()
                data = response.json()

                annotations = data["responses"][0].get("textAnnotations", [])
                text = annotations[0]["description"] if annotations else ""

                return OCRResult(
                    provider="google_vision",
                    text=text,
                    confidence=0.95,
                    success=True,
                )

        except Exception as e:
            return OCRResult(
                provider="google_vision",
                text="",
                success=False,
                error=str(e),
            )

    async def _get_access_token(self) -> str:
        import time
        import jwt

        if not settings.GOOGLE_APPLICATION_CREDENTIALS:
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set")

        with open(settings.GOOGLE_APPLICATION_CREDENTIALS, "r") as f:
            creds = json.load(f)

        now = int(time.time())

        payload = {
            "iss": creds["client_email"],
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600,
        }

        token = jwt.encode(payload, creds["private_key"], algorithm="RS256")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": token,
                },
            )

            response.raise_for_status()
            return response.json()["access_token"]


# ===================== GEMINI OCR =====================
class GeminiOCRService(BaseOCRService):
    async def extract_text(self, image_base64: str) -> OCRResult:
        try:
            if not settings.GEMINI_API_KEY:
                raise Exception("GEMINI_API_KEY not set")

            models = [
                "gemini-2.0-flash",
                "gemini-1.5-flash",
                "gemini-1.5-flash-latest",
            ]

            async with httpx.AsyncClient(timeout=30) as client:
                for model in models:
                    try:
                        response = await client.post(
                            f"https://generativelanguage.googleapis.com/v1beta/models/"
                            f"{model}:generateContent?key={settings.GEMINI_API_KEY}",
                            json={
                                "contents": [{
                                    "parts": [
                                        {"text": "Extract all text from this image. Return only the raw text."},
                                        {
                                            "inline_data": {
                                                "mime_type": "image/jpeg",
                                                "data": image_base64
                                            }
                                        },
                                    ]
                                }]
                            },
                        )

                        if response.status_code == 200:
                            data = response.json()
                            text = data["candidates"][0]["content"]["parts"][0]["text"]

                            return OCRResult(
                                provider="gemini",
                                text=text,
                                confidence=0.92,
                                success=True,
                            )

                    except Exception:
                        continue

            raise Exception("All Gemini models failed")

        except Exception as e:
            return OCRResult(
                provider="gemini",
                text="",
                success=False,
                error=str(e),
            )