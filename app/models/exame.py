from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.db.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.consulta import Consulta

class Exame(Base):
    __tablename__ = "exames"

    id: Mapped[int] = mapped_column(primary_key=True)

    tipo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    resultado: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    consulta_id: Mapped[int] = mapped_column(
        ForeignKey("consultas.id", ondelete="CASCADE"),
        nullable=False
    )

    consulta: Mapped["Consulta"] = relationship(
        back_populates="exames"
    )