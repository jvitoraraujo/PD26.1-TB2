from datetime import datetime

from pydantic import BaseModel

class ConsultaCreate(BaseModel):

    paciente_id: int

class ConsultaResponse(BaseModel):

    id: int

    data_consulta: datetime

    paciente_id: int

    model_config = {
        "from_attributes": True
    }