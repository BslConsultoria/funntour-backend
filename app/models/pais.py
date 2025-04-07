from sqlalchemy import Column, Integer, String, DateTime, func
from app.config.database import Base
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Pais(Base):
    __tablename__ = "pais"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    descricao = Column(String(255), nullable=False)
    sigla = Column(String(10), nullable=False)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)

    def __init__(self, descricao, sigla):
        self.descricao = descricao
        self.sigla = sigla
        logger.info(f"Objeto País criado: {descricao} ({sigla})")

    def update(self, descricao=None, sigla=None):
        if descricao is not None:
            self.descricao = descricao
        if sigla is not None:
            self.sigla = sigla
        logger.info(f"País atualizado: ID {self.id}")
        return self

    def delete(self):
        self.dt_exclusao = func.now()
        logger.info(f"País excluído (soft delete): ID {self.id}")
        return self

    def __repr__(self):
        return f"<Pais(id={self.id}, descricao='{self.descricao}', sigla='{self.sigla}')>"
