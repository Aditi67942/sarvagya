from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # -------------------------------
    # APP CONFIG
    # -------------------------------
    PROJECT_NAME: str = "Sarvagya"
    API_V1_STR: str = "/api/v1"

    # -------------------------------
    # API KEYS (Optional for now)
    # -------------------------------
    sarvam_api_key: str | None = None
    gemini_api_key: str | None = None
    google_application_credentials: str | None = None

    # -------------------------------
    # FILE UPLOAD CONFIG
    # -------------------------------
    allowed_extensions_list: list[str] = [
        "jpg",
        "jpeg",
        "png",
        "pdf",
        "tiff"
    ]

    max_upload_size_mb: int = 5
    max_upload_size_bytes: int = 5 * 1024 * 1024

    upload_dir: str = "uploads"

    # -------------------------------
    # ENV CONFIG
    # -------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()