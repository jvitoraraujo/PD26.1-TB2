from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.exame import Exame
    from app.models.medico import Medico
    from app.models.paciente import Paciente


class Consulta(Base):
    __tablename__ = "consultas"

    id: Mapped[int] = mapped_column(primary_key=True)

    data_consulta: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    diagnostico: Mapped[str | None] = mapped_column(Text, nullable=True)

    # FK para Paciente (many-to-one)
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id"),
        nullable=False,
    )

    # FK para Medico (many-to-one)
    medico_id: Mapped[int | None] = mapped_column(
        ForeignKey("medicos.id"),
        nullable=True,
    )

    # Relacionamento many-to-one com Paciente
    paciente: Mapped["Paciente"] = relationship(
        back_populates="consultas",
        lazy="joined",
    )

    # Relacionamento many-to-one com Medico
    medico: Mapped["Medico | None"] = relationship(
        back_populates="consultas",
        lazy="joined",
    )

    # Relacionamento one-to-many com Exame
    exames: Mapped[list["Exame"]] = relationship(
        back_populates="consulta",
        lazy="selectin",
        cascade="all, delete-orphan",
    )