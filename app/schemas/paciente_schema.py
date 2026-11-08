from pydantic import BaseModel, EmailStr, Field

from app.schemas.tipos import Cpf, Uf


class PacienteCreate(BaseModel):
    nome: str = Field(min_length=1)
    cpf: Cpf
    telefone: str
    email: EmailStr
    cidade: str
    uf: Uf


class PacienteUpdate(BaseModel):
    nome: str | None = Field(None, min_length=1)
    telefone: str | None = None
    email: EmailStr | None = None
    cidade: str | None = None
    uf: Uf | None = None


class PacienteResponse(BaseModel):
    id: str
    nome: str
    cpf: str
    telefone: str
    email: str
    cidade: str
    uf: str

    @classmethod
    def de_documento(cls, p) -> "PacienteResponse":
        return cls(
            id=str(p.id), nome=p.nome, cpf=p.cpf, telefone=p.telefone,
            email=p.email, cidade=p.cidade, uf=p.uf,
        )
