from datetime import datetime
from beanie import Document, Link

from app.models.medico import Medico
from app.models.paciente import Paciente


class Consulta(Document):
    data_consulta: datetime = datetime.now()

    diagnostico: str | None = None

    paciente: Link[Paciente]
    medico: Link[Medico]

    class Settings:
        name = "consultas"