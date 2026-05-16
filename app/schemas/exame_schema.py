from pydantic import BaseModel


class ExameCreate(BaseModel):
    tipo: str
    resultado: str
    consulta_id: int


class ExameUpdate(BaseModel):
    tipo: str | None = None
    resultado: str | None = None


class ExameResponse(BaseModel):
    id: int
    tipo: str
    resultado: str
    consulta_id: int

    model_config = {
        "from_attributes": True
    }