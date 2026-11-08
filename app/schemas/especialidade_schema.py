from pydantic import BaseModel, Field


class EspecialidadeCreate(BaseModel):
    nome: str = Field(min_length=1)


class EspecialidadeResponse(BaseModel):
    id: str
    nome: str

    @classmethod
    def de_documento(cls, doc) -> "EspecialidadeResponse":
        return cls(id=str(doc.id), nome=doc.nome)
