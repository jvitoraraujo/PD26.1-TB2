from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from sqlalchemy import (
    DateTime,
    ForeignKey
)

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.paciente import Paciente
    from app.models.exame import Exame

class Consulta(Base):
    __tablename__ = "consultas"

    id: Mapped[int] = mapped_column(primary_key=True)

    data_consulta: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id")
    )

    paciente: Mapped["Paciente"] = relationship(
        back_populates="consultas"
    )

    exames: Mapped[list["Exame"]] = relationship(
        back_populates="consulta",
        lazy="selectin",
        cascade="all, delete-orphan"
    )