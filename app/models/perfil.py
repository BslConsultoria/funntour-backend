from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from app.config.database import Base

class Perfil(Base):
    __tablename__ = "perfil"
    
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)
