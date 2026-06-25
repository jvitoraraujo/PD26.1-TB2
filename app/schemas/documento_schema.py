from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str

    original_filename: str
    content_type: str
    extension: str

    size_bytes: int

    created_at: datetime

    paciente_id: str

    model_config = {
        "from_attributes": True
    }