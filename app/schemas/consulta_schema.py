from datetime import datetime
from pydantic import BaseModel


class ConsultaCreate(BaseModel):
    paciente_id: str
    medico_id: str
    diagnostico: str | None = None


class ConsultaResponse(BaseModel):
    id: str

    data_consulta: datetime

    diagnostico: str | None = None

    paciente_id: str
    medico_id: str

    model_config = {
        "from_attributes": True
    }