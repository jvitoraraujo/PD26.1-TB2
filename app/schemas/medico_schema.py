from pydantic import BaseModel, EmailStr, Field


class MedicoCreate(BaseModel):
    nome: str
    crm: str = Field(..., min_length=1)

    telefone: str
    email: EmailStr | None = None

    cidade: str
    uf: str = Field(..., min_length=2, max_length=2)

    ativo: bool = True

    especialidades: list[str]

class MedicoUpdate(BaseModel):
    nome: str | None = None
    crm: str | None = Field(default=None, min_length=1)
 
    telefone: str | None = None
    email: EmailStr | None = None
 
    cidade: str | None = None
    uf: str | None = Field(default=None, min_length=2, max_length=2)
 
    ativo: bool | None = None
 
    especialidades: list[str] | None = None


class MedicoResponse(MedicoCreate):
    id: str

    model_config = {
        "from_attributes": True
    }