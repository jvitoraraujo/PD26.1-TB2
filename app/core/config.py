from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    MONGODB_URL: str
    DATABASE_NAME: str
    MONGODB_TIMEOUT_MS: int = 5000
    UPLOAD_DIR: Path = RAIZ / "uploads_documentos"
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=RAIZ / ".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
