from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Cidade(Base):
    __tablename__ = "cidade"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estado_id = Column(Integer, ForeignKey("estado.id"), nullable=False)
    descricao = Column(String(255), nullable=False)
    sigla = Column(String(10), nullable=True)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)

    # Relacionamento com Estado
    estado = relationship("Estado", lazy="joined")
