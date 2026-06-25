from datetime import datetime

from beanie import Document, Link

from app.models.medico import Medico
from app.models.paciente import Paciente

class Internacao(Document):
    data_entrada: datetime
    data_saida: datetime | None = None

    quarto: str
    motivo: str
    observacoes: str | None = None

    valor_diaria: float

    paciente: Link[Paciente]
    medico: Link[Medico]

    class Settings:
        name = "internacoes"