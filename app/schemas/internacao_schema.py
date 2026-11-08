from pydantic import BaseModel, Field, model_validator

from app.core.crud import link_id
from app.schemas.tipos import DataHora, IdObjeto


def _checar_periodo(entrada, saida) -> None:
    if entrada is not None and saida is not None and saida < entrada:
        raise ValueError("data_saida não pode ser anterior a data_entrada")


class InternacaoCreate(BaseModel):
    paciente_id: IdObjeto
    medico_id: IdObjeto
    data_entrada: DataHora
    data_saida: DataHora | None = None
    quarto: str = Field(min_length=1)
    motivo: str = Field(min_length=1)
    observacoes: str | None = None
    valor_diaria: float = Field(ge=0)

    @model_validator(mode="after")
    def _periodo(self):
        _checar_periodo(self.data_entrada, self.data_saida)
        return self


class InternacaoUpdate(BaseModel):
    data_saida: DataHora | None = None
    quarto: str | None = Field(None, min_length=1)
    motivo: str | None = Field(None, min_length=1)
    observacoes: str | None = None
    valor_diaria: float | None = Field(None, ge=0)


class InternacaoResponse(BaseModel):
    id: str
    data_entrada: DataHora
    data_saida: DataHora | None = None
    quarto: str
    motivo: str
    observacoes: str | None = None
    valor_diaria: float
    paciente_id: str
    medico_id: str

    @classmethod
    def de_documento(cls, i) -> "InternacaoResponse":
        return cls(
            id=str(i.id), data_entrada=i.data_entrada, data_saida=i.data_saida,
            quarto=i.quarto, motivo=i.motivo, observacoes=i.observacoes,
            valor_diaria=i.valor_diaria,
            paciente_id=str(link_id(i.paciente)), medico_id=str(link_id(i.medico)),
        )
