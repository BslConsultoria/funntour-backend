from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.pais import PaisResponse

class EstadoBase(BaseModel):
    pais_id: int = Field(..., gt=0, description="ID do pau00eds ao qual o estado pertence")
    descricao: str = Field(..., min_length=2, max_length=255, description="Nome do estado")
    sigla: str = Field(..., min_length=2, max_length=10, description="Sigla do estado")

    @validator('descricao')
    def descricao_capitalizada(cls, v):
        return v.strip().title()
    
    @validator('sigla')
    def sigla_maiuscula(cls, v):
        return v.strip().upper()

class CreateEstado(EstadoBase):
    pass

class UpdateEstado(BaseModel):
    pais_id: Optional[int] = Field(None, gt=0, description="ID do pau00eds ao qual o estado pertence")
    descricao: Optional[str] = Field(None, min_length=2, max_length=255, description="Nome do estado")
    sigla: Optional[str] = Field(None, min_length=2, max_length=10, description="Sigla do estado")
    
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

class EstadoResponse(EstadoBase):
    id: int
    dt_criacao: datetime
    dt_atualizacao: datetime
    dt_exclusao: Optional[datetime] = None
    pais: Optional[PaisResponse] = None
    
    class Config:
        orm_mode = True

# Este schema foi removido pois agora EstadoResponse já inclui o país relacionado
