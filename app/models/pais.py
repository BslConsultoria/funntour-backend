from sqlalchemy import Column, Integer, String, DateTime, func
from app.config.database import Base

class Pais(Base):
    __tablename__ = "pais"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descricao = Column(String(255), nullable=False)
    sigla = Column(String(10), nullable=False)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)


