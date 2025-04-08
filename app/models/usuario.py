from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Usuario(Base):
    __tablename__ = "usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    endereco_id = Column(Integer, ForeignKey("endereco.id"), nullable=False)
    perfil_id = Column(Integer, ForeignKey("perfil.id"), nullable=False)
    cpf_cnpj = Column(String(20), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefone = Column(String(20), nullable=False)
    whatsapp = Column(String(20), nullable=True)
    dt_nascimento = Column(Date, nullable=False)
    avatar = Column(String(255), nullable=True)
    aceite_termos = Column(Boolean, nullable=False)
    eh_maior_18 = Column(Boolean, nullable=False)
    dt_criacao = Column(DateTime, default=func.now())
    dt_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    dt_exclusao = Column(DateTime, nullable=True)
    
    # Relacionamentos
    endereco = relationship("Endereco", lazy="joined") 
    perfil = relationship("Perfil", lazy="joined")
