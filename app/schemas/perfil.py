from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class PerfilBase(BaseModel):
    descricao: str = Field(..., min_length=2, max_length=255, description="Descrição do perfil de usuário")
    
    @validator('descricao')
    def descricao_capitalizada(cls, v):
        return v.strip().title()

class CreatePerfil(PerfilBase):
    pass

class UpdatePerfil(BaseModel):
    descricao: Optional[str] = Field(None, min_length=2, max_length=255, description="Descrição do perfil de usuário")
    
    @validator('descricao')
    def descricao_capitalizada(cls, v):
        if v is None:
            return v
        return v.strip().title()

class PerfilResponse(BaseModel):
    id: int
    descricao: str
    dt_criacao: datetime
    dt_atualizacao: datetime
    dt_exclusao: Optional[datetime] = None
    
    class Config:
        from_attributes = True
