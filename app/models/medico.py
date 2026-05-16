from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.internacao import Internacao


class Medico(Base):
    """Representa um médico no sistema hospitalar."""

    __tablename__ = "medicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    crm = Column(String, unique=True, index=True, nullable=False)
    especialidade = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    cidade = Column(String, nullable=False)
    uf = Column(String(2), nullable=False)
    ativo = Column(Boolean, default=True)

    # Relacionamento one-to-many com Internacao
    internacoes: Mapped[list["Internacao"]] = relationship(
        back_populates="medico",
        lazy="selectin",
    )