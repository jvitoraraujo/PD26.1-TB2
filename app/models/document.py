from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    extension = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relação com Paciente (Pode adaptar para Medico, Consulta, etc.)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)