from beanie import Document
from pymongo import ASCENDING, IndexModel


class Especialidade(Document):
    nome: str

    class Settings:
        name = "especialidades"
        indexes = [IndexModel([("nome", ASCENDING)], unique=True)]
