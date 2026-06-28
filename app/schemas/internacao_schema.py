from datetime import datetime
from pydantic import BaseModel, Field


class InternacaoCreate(BaseModel):
    data_entrada: datetime
    data_saida: datetime | None = None

    quarto: str
    motivo: str
    observacoes: str | None = None

    valor_diaria: float = Field(..., gt=0)

    paciente_id: str
    medico_id: str


class InternacaoUpdate(BaseModel):
    data_entrada: datetime | None = None
    data_saida: datetime | None = None

    quarto: str | None = None
    motivo: str | None = None
    observacoes: str | None = None

    valor_diaria: float | None = Field(default=None, gt=0)

    paciente_id: str | None = None
    medico_id: str | None = None


class InternacaoResponse(BaseModel):
    id: str

    data_entrada: datetime
    data_saida: datetime | None = None

    quarto: str
    motivo: str
    observacoes: str | None = None

    valor_diaria: float

    paciente_id: str
    medico_id: str

    model_config = {
        "from_attributes": True
    }