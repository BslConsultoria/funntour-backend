from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Estado(Base):
    __tablename__ = "estado"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pais_id = Column(Integer, ForeignKey("pais.id"), nullable=False)
    descricao = Column(String(255), nullable=False)
    sigla = Column(String(10), nullable=False)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)

    # Relacionamento com Pais
    pais = relationship("Pais", lazy="joined")
