from pydantic import BaseModel, EmailStr, Field

from app.models.especialidade import Especialidade
from app.schemas.especialidade_schema import EspecialidadeResponse
from app.schemas.tipos import IdObjeto, Uf


class MedicoCreate(BaseModel):
    nome: str = Field(min_length=1)
    crm: str = Field(min_length=1)

    telefone: str
    email: EmailStr | None = None

    cidade: str
    uf: Uf

    ativo: bool = True

    especialidades: list[IdObjeto]


class MedicoResponse(BaseModel):
    id: str
    nome: str
    crm: str
    telefone: str
    email: str | None = None
    cidade: str
    uf: str
    ativo: bool
    especialidades: list[EspecialidadeResponse]

    @classmethod
    def de_documento(cls, m) -> "MedicoResponse":
        """Espera as especialidades carregadas (fetch_links ou documentos atribuídos)."""
        return cls(
            id=str(m.id), nome=m.nome, crm=m.crm, telefone=m.telefone, email=m.email,
            cidade=m.cidade, uf=m.uf, ativo=m.ativo,
            especialidades=[
                EspecialidadeResponse.de_documento(e)
                for e in m.especialidades
                if isinstance(e, Especialidade)
            ],
        )
