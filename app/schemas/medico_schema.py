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


class MedicoResponse(MedicoCreate):
    id: str

    model_config = {
        "from_attributes": True
    }