from pydantic import BaseModel


class EspecialidadeCreate(BaseModel):
    nome: str


class EspecialidadeResponse(BaseModel):
    id: str
    nome: str

    model_config = {
        "from_attributes": True
    }