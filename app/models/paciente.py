from beanie import Document

class Paciente(Document):
    nome: str
    cpf: str
    telefone: str
    email: str
    cidade: str
    uf: str

    class Settings:
        name = "pacientes"