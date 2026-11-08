from beanie import Document, Link
from pymongo import ASCENDING, IndexModel

from app.models.especialidade import Especialidade


class Medico(Document):
    nome: str
    crm: str
    telefone: str
    email: str | None = None
    cidade: str
    uf: str
    ativo: bool = True

    especialidades: list[Link[Especialidade]]

    class Settings:
        name = "medicos"
        indexes = [IndexModel([("crm", ASCENDING)], unique=True)]
