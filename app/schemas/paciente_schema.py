from pydantic import BaseModel, EmailStr


class PacienteCreate(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: EmailStr
    cidade: str
    uf: str


class PacienteUpdate(BaseModel):
    nome: str | None = None
    telefone: str | None = None
    email: EmailStr | None = None
    cidade: str | None = None
    uf: str | None = None


class PacienteResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str
    email: str
    cidade: str
    uf: str

    model_config = {
        "from_attributes": True
    }