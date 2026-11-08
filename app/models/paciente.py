from beanie import Document
from pymongo import ASCENDING, IndexModel


class Paciente(Document):
    nome: str
    cpf: str
    telefone: str
    email: str
    cidade: str
    uf: str

    class Settings:
        name = "pacientes"
        indexes = [IndexModel([("cpf", ASCENDING)], unique=True)]
