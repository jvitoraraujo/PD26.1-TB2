from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.db.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.consulta import Consulta

class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(primary_key=True)

    nome: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    cpf: Mapped[str] = mapped_column(
        String(14),
        unique=True,
        nullable=False
    )

    telefone: Mapped[str] = mapped_column(
        String(20)
    )

    email: Mapped[str] = mapped_column(
        String(100)
    )

    cidade: Mapped[str] = mapped_column(
        String(100)
    )

    uf: Mapped[str] = mapped_column(
        String(2)
    )

    consultas: Mapped[list["Consulta"]] = relationship(
        back_populates="paciente",
        lazy="selectin",
        cascade="all, delete-orphan"
    )