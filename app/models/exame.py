from beanie import Document, Link

from app.models.consulta import Consulta

class Exame(Document):
    tipo: str
    resultado: str

    consulta: Link[Consulta]

    class Settings:
        name = "exames"