from datetime import datetime, timezone

from beanie import Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.models.medico import Medico
from app.models.paciente import Paciente


class Consulta(Document):
    data_consulta: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    diagnostico: str | None = None

    paciente: Link[Paciente]
    medico: Link[Medico]

    class Settings:
        name = "consultas"
        indexes = [IndexModel([("data_consulta", ASCENDING)])]
