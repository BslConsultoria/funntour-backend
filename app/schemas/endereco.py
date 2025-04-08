from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from app.schemas.cidade import CidadeResponse
from app.schemas.estado import EstadoResponse

class EnderecoBase(BaseModel):
    cidade_id: int = Field(..., gt=0, description="ID da cidade do endereu00e7o")
    cep: Optional[str] = Field(None, max_length=20, description="CEP do endereu00e7o")
    complemento: Optional[str] = Field(None, max_length=255, description="Complemento do endereu00e7o")
    
    @validator('cep')
    def formatar_cep(cls, v):
        if v is None:
            return v
        # Remove caracteres nu00e3o numu00e9ricos e formata o CEP
        cep_limpo = ''.join(filter(str.isdigit, v))
        if len(cep_limpo) == 8:
            return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_limpo

class CreateEndereco(EnderecoBase):
    pass

class UpdateEndereco(BaseModel):
    cidade_id: Optional[int] = Field(None, gt=0, description="ID da cidade do endereu00e7o")
    cep: Optional[str] = Field(None, max_length=20, description="CEP do endereu00e7o")
    complemento: Optional[str] = Field(None, max_length=255, description="Complemento do endereu00e7o")
    
    @validator('cep')
    def formatar_cep(cls, v):
        if v is None:
            return v
        # Remove caracteres nu00e3o numu00e9ricos e formata o CEP
        cep_limpo = ''.join(filter(str.isdigit, v))
        if len(cep_limpo) == 8:
            return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep_limpo

class EnderecoResponse(BaseModel):
    id: int
    cidade_id: int
    cep: Optional[str] = None
    complemento: Optional[str] = None
    dt_criacao: datetime
    dt_atualizacao: datetime
    dt_exclusao: Optional[datetime] = None
    cidade: Optional[CidadeResponse] = None
    
    class Config:
        from_attributes = True
