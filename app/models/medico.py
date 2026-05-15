from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class Medico(Base):
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