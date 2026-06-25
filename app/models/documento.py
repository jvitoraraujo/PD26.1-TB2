from datetime import datetime

from beanie import Document, Link

from app.models.paciente import Paciente


class Documento(Document):
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int

    created_at: datetime = datetime.now()

    paciente: Link[Paciente]

    class Settings:
        name = "documents"