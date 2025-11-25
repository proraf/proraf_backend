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


class WhatsAppProductUpdate(BaseModel):
    """Schema para edição de produto via WhatsApp"""
    telefone: str = Field(..., min_length=10, max_length=20)
    hash: str = Field(...)
    product_id: int = Field(..., description="ID do produto a ser editado")
    name: Optional[str] = Field(None, min_length=3, max_length=255, description="Novo nome do produto")
    comertial_name: Optional[str] = Field(None, max_length=255, description="Novo nome comercial")
    description: Optional[str] = Field(None, max_length=500, description="Nova descrição")
    variedade_cultivar: Optional[str] = Field(None, max_length=255, description="Nova variedade ou cultivar")
    status: Optional[bool] = Field(None, description="Status ativo/inativo")


class WhatsAppBatchCreate(BaseModel):
    """Schema para criação de lote via WhatsApp"""
    telefone: str = Field(..., min_length=10, max_length=20)
    hash: str = Field(...)
    product_id: int = Field(..., description="ID do produto ao qual o lote pertence")
    talhao: Optional[str] = Field(None, max_length=100, description="Identificação do talhão")
    dt_plantio: Optional[str] = Field(None, description="Data de plantio (formato: YYYY-MM-DD)")
    dt_colheita: Optional[str] = Field(None, description="Data prevista de colheita (formato: YYYY-MM-DD)")
    producao: Optional[float] = Field(None, ge=0, description="Quantidade produzida")
    unidadeMedida: Optional[str] = Field(None, max_length=50, description="Unidade de medida (kg, ton, sc, etc)")


class WhatsAppBatchResponse(BaseModel):
    """Schema para resposta de criação de lote via WhatsApp"""
    success: bool
    message: str
    batch_id: Optional[int] = None
    batch_code: Optional[str] = None
    product_name: Optional[str] = None
    qrcode_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ProductListItem(BaseModel):
    """Schema para item na lista de produtos"""
    id: int
    name: str
    comertial_name: Optional[str] = None
    description: Optional[str] = None
    variedade_cultivar: Optional[str] = None
    status: bool
    code: str
    batches_count: int = 0
    
    class Config:
        from_attributes = True


class WhatsAppProductListResponse(BaseModel):
    """Schema para resposta de listagem de produtos via WhatsApp"""
    success: bool
    message: str
    total_products: int
    active_products: int
    inactive_products: int
    products: list[ProductListItem]
    
    class Config:
        from_attributes = True
