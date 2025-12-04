from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    tipo_pessoa: str = Field(..., pattern="^(F|J|N)$")
    cpf: Optional[str] = Field(None, max_length=14)
    cnpj: Optional[str] = Field(None, max_length=18)
    nit: Optional[str] = Field(None, max_length=11)  # NIT - Número de Inscrição do Trabalhador
    telefone: Optional[str] = Field(None, max_length=20)
    tipo_perfil: str = Field(default="user")
    
    @field_validator('tipo_pessoa')
    @classmethod
    def validate_tipo_pessoa(cls, v):
        if v not in ['F', 'J', 'N']:
            raise ValueError('tipo_pessoa deve ser F (Física), J (Jurídica) ou N (NIT)')
        return v


class UserCreate(UserBase):
    senha: str = Field(..., min_length=6)
    
    @model_validator(mode='after')
    def validate_document(self):
        tipo_pessoa = self.tipo_pessoa
        cpf = self.cpf
        cnpj = self.cnpj
        nit = self.nit
        
        if tipo_pessoa == 'F' and not cpf:
            raise ValueError('CPF é obrigatório para pessoa física')
        if tipo_pessoa == 'J' and not cnpj:
            raise ValueError('CNPJ é obrigatório para pessoa jurídica')
        if tipo_pessoa == 'N' and not nit:
            raise ValueError('NIT é obrigatório para trabalhador')
        
        return self


class UserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    senha: Optional[str] = Field(None, min_length=6)
    tipo_perfil: Optional[str] = Field(None)
    
    
class UserUpdateCpfOuCnpj(BaseModel):
    cpfouCnpj: str = Field(..., min_length=11, max_length=18)
    tipoPessoa: str = Field(..., pattern="^(F|J|N)$")
    
    
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