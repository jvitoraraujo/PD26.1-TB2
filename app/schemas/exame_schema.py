from pydantic import BaseModel


class ExameCreate(BaseModel):
    tipo: str
    resultado: str
    consulta_id: str


class ExameUpdate(BaseModel):
    tipo: str | None = None
    resultado: str | None = None


class ExameResponse(BaseModel):
    id: str
    tipo: str
    resultado: str
    consulta_id: str

    model_config = {
        "from_attributes": True
    }