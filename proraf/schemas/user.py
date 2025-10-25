from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    tipo_pessoa: str = Field(..., pattern="^(F|J)$")
    cpf: Optional[str] = Field(None, max_length=14)
    cnpj: Optional[str] = Field(None, max_length=18)
    telefone: Optional[str] = Field(None, max_length=20)
    tipo_perfil: str = Field(default="user")
    
    @validator('tipo_pessoa')
    def validate_tipo_pessoa(cls, v):
        if v not in ['F', 'J']:
            raise ValueError('tipo_pessoa deve ser F (Física) ou J (Jurídica)')
        return v
    
    @validator('cpf')
    def validate_cpf(cls, v, values):
        # Para usuários OAuth (Google), CPF/CNPJ não são obrigatórios
        # Apenas validar se estiver criando usuário local (com senha)
        return v
    
    @validator('cnpj')
    def validate_cnpj(cls, v, values):
        # Para usuários OAuth (Google), CPF/CNPJ não são obrigatórios  
        # Apenas validar se estiver criando usuário local (com senha)
        return v


class UserCreate(UserBase):
    senha: str = Field(..., min_length=6)
    
    @validator('cpf')
    def validate_cpf_create(cls, v, values):
        # Para criação de usuários locais, CPF é obrigatório para PF
        if values.get('tipo_pessoa') == 'F' and not v:
            raise ValueError('CPF é obrigatório para pessoa física')
        return v
    
    @validator('cnpj') 
    def validate_cnpj_create(cls, v, values):
        # Para criação de usuários locais, CNPJ é obrigatório para PJ
        if values.get('tipo_pessoa') == 'J' and not v:
            raise ValueError('CNPJ é obrigatório para pessoa jurídica')
        return v


class UserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    senha: Optional[str] = Field(None, min_length=6)
    tipo_perfil: Optional[str] = Field(None)
    
    
class UserUpdateCpfOuCnpj(BaseModel):
    cpfouCnpj: str = Field(..., min_length=11, max_length=18)
    tipoPessoa: str = Field(..., pattern="^(F|J)$")
    
    
class UserResponse(UserBase):
    id: int
    google_id: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: str = "local"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoogleUserCreate(BaseModel):
    """Schema para criar usuário via Google OAuth"""
    google_id: str
    nome: str
    email: EmailStr
    avatar_url: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None