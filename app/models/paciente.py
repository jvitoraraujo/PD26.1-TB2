from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.consulta import Consulta
    from app.models.internacao import Internacao


class Paciente(Base):
    """Representa um paciente no sistema hospitalar."""

    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)

    telefone: Mapped[str] = mapped_column(String(20))

    email: Mapped[str] = mapped_column(String(100))

    cidade: Mapped[str] = mapped_column(String(100))

    uf: Mapped[str] = mapped_column(String(2))

    # Relacionamento one-to-many com Consulta
    consultas: Mapped[list["Consulta"]] = relationship(
        back_populates="paciente",
        lazy="selectin",
    )

    # Relacionamento one-to-many com Internacao
    internacoes: Mapped[list["Internacao"]] = relationship(
        back_populates="paciente",
        lazy="selectin",
    )