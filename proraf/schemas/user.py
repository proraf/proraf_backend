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
        if values.get('tipo_pessoa') == 'F' and not v:
            raise ValueError('CPF é obrigatório para pessoa física')
        return v
    
    @validator('cnpj')
    def validate_cnpj(cls, v, values):
        if values.get('tipo_pessoa') == 'J' and not v:
            raise ValueError('CNPJ é obrigatório para pessoa jurídica')
        return v


class UserCreate(UserBase):
    senha: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    senha: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None