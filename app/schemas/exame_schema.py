from pydantic import BaseModel, Field

from app.core.crud import link_id
from app.schemas.tipos import IdObjeto


class ExameCreate(BaseModel):
    tipo: str = Field(min_length=1)
    resultado: str
    consulta_id: IdObjeto


class ExameUpdate(BaseModel):
    tipo: str | None = Field(None, min_length=1)
    resultado: str | None = None


class ExameResponse(BaseModel):
    id: str
    tipo: str
    resultado: str
    consulta_id: str

    @classmethod
    def de_documento(cls, e) -> "ExameResponse":
        return cls(id=str(e.id), tipo=e.tipo, resultado=e.resultado, consulta_id=str(link_id(e.consulta)))
