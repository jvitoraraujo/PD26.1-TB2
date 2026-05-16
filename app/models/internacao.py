from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.medico import Medico
    from app.models.paciente import Paciente


class Internacao(Base):
    """Representa uma internação hospitalar no sistema."""

    __tablename__ = "internacoes"

    id: Mapped[int] = mapped_column(primary_key=True)

    data_entrada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    data_saida: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    quarto: Mapped[str] = mapped_column(String(20), nullable=False)

    motivo: Mapped[str] = mapped_column(String(255), nullable=False)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    valor_diaria: Mapped[float] = mapped_column(nullable=False, default=0.0)

    # FK para Paciente (many-to-one)
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id"),
        nullable=False,
    )

    # FK para Medico responsável (many-to-one)
    medico_id: Mapped[int] = mapped_column(
        ForeignKey("medicos.id"),
        nullable=False,
    )

    # Relacionamento many-to-one com Paciente
    paciente: Mapped["Paciente"] = relationship(
        back_populates="internacoes",
        lazy="joined",
    )

    # Relacionamento many-to-one com Medico
    medico: Mapped["Medico"] = relationship(
        back_populates="internacoes",
        lazy="joined",
    )