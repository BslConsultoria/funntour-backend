from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional
from datetime import datetime, date
from app.schemas.endereco import EnderecoResponse, EnderecoBase, UpdateEndereco
from app.schemas.perfil import PerfilResponse

class UsuarioBase(BaseModel):
    endereco: EnderecoBase = Field(..., description="Dados do endereu00e7o para criação junto com o usuário")
    perfil_id: int = Field(..., gt=0, description="ID do perfil do usuu00e1rio")
    cpf_cnpj: str = Field(..., min_length=11, max_length=20, description="CPF ou CNPJ do usuu00e1rio")
    nome: str = Field(..., min_length=2, max_length=255, description="Nome completo do usuu00e1rio")
    email: Optional[EmailStr] = Field(None, description="Email do usuu00e1rio")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone do usuu00e1rio")
    whatsapp: Optional[str] = Field(None, max_length=20, description="WhatsApp do usuu00e1rio")
    dt_nascimento: Optional[date] = Field(None, description="Data de nascimento do usuu00e1rio")
    avatar: Optional[str] = Field(None, max_length=255, description="URL do avatar do usuu00e1rio")
    aceite_termos: Optional[bool] = Field(None, description="Indica se o usuu00e1rio aceitou os termos de uso")
    eh_maior_18: Optional[bool] = Field(None, description="Indica se o usuu00e1rio u00e9 maior de 18 anos")
    
    @validator('nome')
    def nome_capitalizado(cls, v):
        return " ".join(word.capitalize() for word in v.strip().split())
    
    @validator('cpf_cnpj')
    def formatar_cpf_cnpj(cls, v):
        # Remove caracteres nu00e3o numu00e9ricos
        numeros = ''.join(filter(str.isdigit, v))
        # Verifica se u00e9 CPF ou CNPJ pelo tamanho
        if len(numeros) == 11:  # CPF
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        elif len(numeros) == 14:  # CNPJ
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        return numeros
    
    @validator('telefone', 'whatsapp')
    def formatar_telefone(cls, v, values, **kwargs):
        if v is None:
            return v
        # Remove caracteres nu00e3o numu00e9ricos
        numeros = ''.join(filter(str.isdigit, v))
        # Formata o telefone
        if len(numeros) == 10:  # Telefone fixo sem DDD
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        elif len(numeros) == 11:  # Celular com DDD
            return f"({numeros[:2]}) {numeros[2:3]} {numeros[3:7]}-{numeros[7:]}"
        return numeros

class CreateUsuario(UsuarioBase):
    senha: str = Field(..., min_length=6, description="Senha do usuu00e1rio")

class UpdateUsuario(BaseModel):
    endereco: Optional[UpdateEndereco] = Field(None, description="Dados do endereu00e7o para atualização junto com o usuário")
    perfil_id: Optional[int] = Field(None, gt=0, description="ID do perfil do usuu00e1rio")
    nome: Optional[str] = Field(None, min_length=2, max_length=255, description="Nome completo do usuu00e1rio")
    email: Optional[EmailStr] = Field(None, description="Email do usuu00e1rio")
    telefone: Optional[str] = Field(None, max_length=20, description="Telefone do usuu00e1rio")
    whatsapp: Optional[str] = Field(None, max_length=20, description="WhatsApp do usuu00e1rio")
    dt_nascimento: Optional[date] = Field(None, description="Data de nascimento do usuu00e1rio")
    avatar: Optional[str] = Field(None, max_length=255, description="URL do avatar do usuu00e1rio")
    aceite_termos: Optional[bool] = Field(None, description="Indica se o usuu00e1rio aceitou os termos de uso")
    eh_maior_18: Optional[bool] = Field(None, description="Indica se o usuu00e1rio u00e9 maior de 18 anos")
    senha: Optional[str] = Field(None, min_length=6, description="Nova senha do usuu00e1rio")
    
    @validator('nome')
    def nome_capitalizado(cls, v):
        if v is None:
            return v
        return " ".join(word.capitalize() for word in v.strip().split())
    
    @validator('telefone', 'whatsapp')
    def formatar_telefone(cls, v, values, **kwargs):
        if v is None:
            return v
        # Remove caracteres nu00e3o numu00e9ricos
        numeros = ''.join(filter(str.isdigit, v))
        # Formata o telefone
        if len(numeros) == 10:  # Telefone fixo sem DDD
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        elif len(numeros) == 11:  # Celular com DDD
            return f"({numeros[:2]}) {numeros[2:3]} {numeros[3:7]}-{numeros[7:]}"
        return numeros

class UsuarioResponse(BaseModel):
    id: int
    endereco_id: int
    perfil_id: int
    cpf_cnpj: str
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    dt_nascimento: Optional[date] = None
    avatar: Optional[str] = None
    aceite_termos: Optional[bool] = None
    eh_maior_18: Optional[bool] = None
    dt_criacao: datetime
    dt_atualizacao: datetime
    dt_exclusao: Optional[datetime] = None
    endereco: Optional[EnderecoResponse] = None
    perfil: Optional[PerfilResponse] = None
    
    class Config:
        from_attributes = True

class UsuarioAuth(BaseModel):
    cpf_cnpj: str
    senha: str
