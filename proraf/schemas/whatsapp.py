from typing import Optional
from pydantic import BaseModel, Field


class WhatsAppAuth(BaseModel):
    """Schema para autenticação via WhatsApp"""
    telefone: str = Field(..., min_length=10, max_length=20, description="Número de telefone do usuário")
    hash: str = Field(..., description="Hash compartilhado para autenticação")


class PhoneVerification(BaseModel):
    """Schema para verificação de telefone"""
    telefone: str = Field(..., min_length=10, max_length=20)
    hash: str = Field(...)


class PhoneResponse(BaseModel):
    """Schema para resposta de verificação de telefone"""
    exists: bool
    user_id: Optional[int] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    tipo_pessoa: Optional[str] = None


class WhatsAppProductCreate(BaseModel):
    """Schema para criação de produto via WhatsApp"""
    telefone: str = Field(..., min_length=10, max_length=20)
    hash: str = Field(...)
    name: str = Field(..., min_length=3, max_length=255, description="Nome do produto")
    description: Optional[str] = Field(None, max_length=500, description="Descrição do produto")
    variedade_cultivar: Optional[str] = Field(None, max_length=255, description="Variedade ou cultivar")


class WhatsAppProductResponse(BaseModel):
    """Schema para resposta de criação de produto via WhatsApp"""
    success: bool
    message: str
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    qrcode_url: Optional[str] = None
    
    class Config:
        from_attributes = True
