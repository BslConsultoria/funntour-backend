from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base
from app.models.cidade import Cidade
from app.models.estado import Estado

class Endereco(Base):
    __tablename__ = "endereco"
    
    id = Column(Integer, primary_key=True, index=True)
    cidade_id = Column(Integer, ForeignKey("cidade.id"), nullable=False)
    cep = Column(String(20), nullable=False)
    complemento = Column(String(255), nullable=False)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)
    
    # Relacionamentos
    cidade = relationship("Cidade", lazy="joined")
