from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.estado import EstadoResponse

class CidadeBase(BaseModel):
    estado_id: int = Field(..., gt=0, description="ID do estado ao qual a cidade pertence")
    descricao: str = Field(..., min_length=2, max_length=255, description="Nome da cidade")
    sigla: Optional[str] = Field(None, max_length=10, description="Sigla ou código da cidade")

    @validator('descricao')
    def descricao_capitalizada(cls, v):
        return v.strip().title()

class CreateCidade(CidadeBase):
    pass

class UpdateCidade(BaseModel):
    estado_id: Optional[int] = Field(None, gt=0, description="ID do estado ao qual a cidade pertence")
    descricao: Optional[str] = Field(None, min_length=2, max_length=255, description="Nome da cidade")
    sigla: Optional[str] = Field(None, max_length=10, description="Sigla ou código da cidade")
    
    @validator('descricao', 'sigla')
    def capitalizar_campos(cls, v, values, **kwargs):
        if v is None:
            return v
        if kwargs['field'].name == 'descricao':
            return v.strip().title()
        else:  # sigla
            return v.strip().upper() if v else None

class CidadeResponse(BaseModel):
    id: int
    estado_id: int = Field(..., description="ID do estado ao qual a cidade pertence")
    descricao: str = Field(..., description="Nome da cidade")
    sigla: Optional[str] = Field(None, description="Sigla ou código da cidade")
    dt_criacao: datetime
    dt_atualizacao: datetime
    dt_exclusao: Optional[datetime] = None
    estado: Optional[EstadoResponse] = None
    
    class Config:
        orm_mode = True

# Este schema foi removido pois agora CidadeResponse já inclui o estado e o país relacionados
