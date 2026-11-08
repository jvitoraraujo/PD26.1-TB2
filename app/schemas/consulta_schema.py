from datetime import datetime

from pydantic import BaseModel

from app.core.crud import link_id
from app.schemas.tipos import DataHora, IdObjeto


class ConsultaCreate(BaseModel):
    paciente_id: IdObjeto
    medico_id: IdObjeto
    diagnostico: str | None = None
    data_consulta: DataHora | None = None  # padrão: momento da criação


class ConsultaUpdate(BaseModel):
    paciente_id: IdObjeto | None = None
    medico_id: IdObjeto | None = None
    diagnostico: str | None = None
    data_consulta: DataHora | None = None


class ConsultaResponse(BaseModel):
    id: str
    data_consulta: datetime
    diagnostico: str | None = None
    paciente_id: str
    medico_id: str

    @classmethod
    def de_documento(cls, c) -> "ConsultaResponse":
        return cls(
            id=str(c.id), data_consulta=c.data_consulta, diagnostico=c.diagnostico,
            paciente_id=str(link_id(c.paciente)), medico_id=str(link_id(c.medico)),
        )
