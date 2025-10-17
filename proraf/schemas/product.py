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
    
    @validator('image')
    def validate_image_url(cls, v):
        if v is not None and v.strip():
            # Validação básica de URL
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('data:')):
                raise ValueError('URL da imagem deve começar com http://, https:// ou data:')
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
    
    @validator('image')
    def validate_image_url(cls, v):
        if v is not None and v.strip():
            # Validação básica de URL
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('data:')):
                raise ValueError('URL da imagem deve começar com http://, https:// ou data:')
        return v


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True