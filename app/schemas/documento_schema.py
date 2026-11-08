from datetime import datetime

from pydantic import BaseModel

from app.core.crud import link_id


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    created_at: datetime
    paciente_id: str

    @classmethod
    def de_documento(cls, d) -> "DocumentResponse":
        return cls(
            id=str(d.id), original_filename=d.original_filename, content_type=d.content_type,
            extension=d.extension, size_bytes=d.size_bytes, created_at=d.created_at,
            paciente_id=str(link_id(d.paciente)),
        )
