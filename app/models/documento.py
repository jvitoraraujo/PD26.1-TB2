from datetime import datetime, timezone

from beanie import Document, Link
from pydantic import Field

from app.models.paciente import Paciente


class Documento(Document):
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    paciente: Link[Paciente]

    class Settings:
        name = "documents"
