from beanie import Document

class Especialidade(Document):
    nome: str

    class Settings:
        name = "especialidades"