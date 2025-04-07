from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PaisBase(BaseModel):
    descricao: str = Field(..., min_length=2, max_length=255, description="Nome do país")
    sigla: str = Field(..., min_length=2, max_length=10, description="Sigla do país")

    @validator('descricao')
    def descricao_capitalizada(cls, v):
        return v.strip().title()
    
    @validator('sigla')
    def sigla_maiuscula(cls, v):
        return v.strip().upper()

class CreatePais(PaisBase):
    pass

class UpdatePais(BaseModel):
    descricao: Optional[str] = Field(None, min_length=2, max_length=255, description="Nome do país")
    sigla: Optional[str] = Field(None, min_length=2, max_length=10, description="Sigla do país")
    
    @validator('descricao')
    def descricao_capitalizada(cls, v):
        if v is None:
            return v
        return v.strip().title()
    
    @validator('sigla')
    def sigla_maiuscula(cls, v):
        if v is None:
            return v
        return v.strip().upper()

class PaisResponse(PaisBase):
    id: int
    dt_criacao: datetime
    dt_atualizacao: datetime
    dt_exclusao: Optional[datetime] = None
    
    class Config:
        orm_mode = True
