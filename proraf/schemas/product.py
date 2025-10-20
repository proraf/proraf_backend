from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, validator


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255, description="Nome do produto")
    comertial_name: Optional[str] = Field(None, max_length=255, description="Nome comercial do produto")
    description: Optional[str] = Field(None, description="Descrição detalhada do produto")
    variedade_cultivar: Optional[str] = Field(None, max_length=255, description="Variedade ou cultivar do produto")
    status: bool = Field(True, description="Status ativo/inativo do produto")
    image: Optional[str] = Field(None, max_length=500, description="URL da imagem do produto")
    code: str = Field(..., min_length=1, max_length=50, description="Código único do produto")
    
    @validator('comertial_name', 'description', 'variedade_cultivar')
    def empty_str_to_none(cls, v):
        if v is not None and isinstance(v, str) and not v.strip():
            return None
        return v
    
    @validator('image')
    def validate_image_url(cls, v):
        if v is not None and v.strip():
            # Validação básica de URL - aceita URLs externas ou caminhos locais
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('data:') or v.startswith('/')):
                raise ValueError('URL da imagem deve começar com http://, https://, data: ou ser um caminho local (/)')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255, description="Nome do produto")
    comertial_name: Optional[str] = Field(None, max_length=255, description="Nome comercial do produto")
    description: Optional[str] = Field(None, description="Descrição detalhada do produto")
    variedade_cultivar: Optional[str] = Field(None, max_length=255, description="Variedade ou cultivar do produto")
    status: Optional[bool] = Field(None, description="Status ativo/inativo do produto")
    image: Optional[str] = Field(None, max_length=500, description="URL da imagem do produto")
    
    @validator('comertial_name', 'description', 'variedade_cultivar')
    def empty_str_to_none(cls, v):
        if v is not None and isinstance(v, str) and not v.strip():
            return None
        return v
    
    @validator('image')
    def validate_image_url(cls, v):
        if v is not None and v.strip():
            # Validação básica de URL - aceita URLs externas ou caminhos locais
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('data:') or v.startswith('/')):
                raise ValueError('URL da imagem deve começar com http://, https://, data: ou ser um caminho local (/)')
        return v


class ProductResponse(ProductBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    """Informações básicas do usuário"""
    id: int
    nome: str
    email: str


class ProductWithUserResponse(ProductResponse):
    """Produto com informações do usuário criador"""
    user: UserInfo
    
    class Config:
        from_attributes = True


class ProductImageUpload(BaseModel):
    """Schema para resposta de upload de imagem"""
    image_url: str = Field(..., description="URL da imagem carregada")