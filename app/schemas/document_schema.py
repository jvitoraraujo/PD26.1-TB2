from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    extension: str
    size_bytes: int
    created_at: datetime
    paciente_id: int

    class Config:
        from_attributes = True