import base64


class TTSService:
    async def synthesize(self, text: str):
        try:
            # TEMP MOCK AUDIO (replace later with real API)
            fake_audio = base64.b64encode(f"Audio for: {text}".encode()).decode()

            return {
                "provider": "mock",
                "audio_base64": fake_audio,
                "success": True,
                "error": None,
            }

        except Exception as e:
            return {
                "provider": "mock",
                "audio_base64": "",
                "success": False,
                "error": str(e),
            }